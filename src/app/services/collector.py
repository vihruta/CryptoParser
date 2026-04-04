import uuid
import asyncio

from src.app.domain.protocols import ClientProtocol, StorageProtocol
from src.app.config import Settings
from src.app.domain.models import ErrorItem, ServiceResult, Quote
from src.app.domain.errors import ServiceError, ClientError, ValidationError


class Collector:
    def __init__(self,
                 clients: list[ClientProtocol],
                 storage: StorageProtocol,
                 settings: Settings, 
                 logger):
        self._clients = clients
        self._storage = storage
        self._settings = settings
        self._logger = logger
        self._semaphore = asyncio.Semaphore(self._settings.CONCURRENCY)

    async def _fetch_from_client(self, client, asset: str):
        request_id = str(uuid.uuid4())

        try:
            async with self._semaphore:
                quote = await client.fetch_rate(asset, request_id)
                return quote, None
        
        except (ServiceError, ClientError, ValidationError) as exc:
                msg = f"Error while fetching quote. Error:{str(exc)}. Asset:{asset}. Request_id: {request_id}"
                self._logger.error(
                    msg, asset=asset,
                    request_id=request_id,
                    error=str(exc)
                )

                if self._settings.FAIL_FAST:
                    raise

                return None, ErrorItem(
                                    asset=asset,
                                    source=client.provider,
                                    error_type=exc.__class__.__name__,
                                    error_msg=str(exc)
                                )


    async def collect_quotes_for_asset(self, asset:str):
        quotes = []
        error_list = []

        tasks = [
            asyncio.create_task(self._fetch_from_client(client, asset))
            for client in self._clients
        ]

        try:
            result = await asyncio.gather(*tasks)
        except (ServiceError, ClientError, ValidationError):
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

        for quote, error in result:
            if quote is not None:
                quotes.append(quote)
            
            if error is not None:
                error_list.append(error)

        return quotes, error_list
    

    def normalize_assets(self, assets: list[str]) -> list:
        assets = [asset.strip().upper() for asset in assets if asset.strip()]
        assets = list(dict.fromkeys(assets))
        assets.sort()
        return assets
    

    async def process_assets(self, assets: list[str], 
                             run_id: str) -> ServiceResult:
        if not assets:
            raise ServiceError('No assets!')
        quotes : list[Quote] = []
        errors_list = []
        saved_count = 0
        normalize_assets_list = self.normalize_assets(assets=assets)
        for asset in normalize_assets_list:
            quotes_per_assets, errors_list_per_asset = await self.collect_quotes_for_asset(asset=asset)
            if quotes_per_assets:
                quotes.append(Quote(currency=asset, info=quotes_per_assets))
                saved_count += len(quotes_per_assets)
            errors_list.extend(errors_list_per_asset)
        if quotes:
            await self._storage.save_quotes(run_id, quotes)
        return ServiceResult(run_id=run_id, total_assets=len(normalize_assets_list),
                             saved_count=saved_count, errors=errors_list)
        
    