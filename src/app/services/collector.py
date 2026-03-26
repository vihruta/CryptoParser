from src.app.domain.protocols import ClientProtocol, StorageProtocol
from src.app.config import Settings
from src.app.domain.models import ErrorItem, ServiceResult
from src.app.domain.errors import ServiceError, ClientError

import uuid

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


    async def call_the_client(self, asset:str):
        quotes = []
        error_list = []
        for client in self._clients:
            request_id = str(uuid.uuid4())
            try:
                quote = await client.fetch_rate(asset, request_id)
                quotes.append(quote)
            except (ServiceError, ClientError) as exc:
                msg = "Service Error while processing asset"
                self._logger.error(
                    msg, asset=asset,
                    request_id=request_id,
                    error=str(exc)
                )
                error_list.append(ErrorItem(asset=asset,
                                            source=client.provider,
                                            error_type=exc.__class__.__name__,
                                            error_msg=str(exc)))
                if self._settings.FAIL_FAST:
                    raise
                continue
        return quotes, error_list
    

    def normalize_assets(self, assets: list[str]) -> list:
        normalize_assets_list = []
        for asset in assets:
            normalize_asset_tmp = asset.strip().upper()
            normalize_assets_list.append(normalize_asset_tmp)
        normalize_assets_list = list(dict.fromkeys(normalize_assets_list))
        return normalize_assets_list
    

    async def process_assets(self, assets: list[str], 
                             run_id: str) -> ServiceResult:
        quotes = []
        errors_list = []
        quotes_per_assets = []
        errors_list_per_asset  =[]
        normalize_assets_list = self.normalize_assets(assets=assets)
        for asset in normalize_assets_list:
            quotes_per_assets, errors_list_per_asset = await self.call_the_client(asset=asset)
            quotes.extend(quotes_per_assets)
            errors_list.extend(errors_list_per_asset)
        if quotes:
            await self._storage.save_quotes(run_id, quotes)
        return ServiceResult(run_id=run_id, total_assets=len(normalize_assets_list),
                             saved_count=len(quotes), errors=errors_list)
        
    