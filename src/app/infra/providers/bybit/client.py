import aiohttp
import asyncio

from src.app.domain.errors import ClientError
from src.app.domain.protocols import ClientProtocol
from src.app.domain.models import QuoteInfo
from src.app.config import Settings
from src.app.infra.providers.bybit.mapper import response_validation

class BybitClient(ClientProtocol):
    def __init__(self, session,
                 settings: Settings,
                 logger):
        self._settings = settings
        self._session = session
        self._logger = logger
        self.provider = 'Bybit'
        
    async def fetch_rate(self, asset, request_id) -> QuoteInfo:
        asset = asset + 'USDT'
        for attempt in range(1, self._settings.RETRIES + 1):
            self._logger.info(f'Asset:{asset}, id={request_id}, attempt={attempt}')
            try:
                async with self._session.get(self._settings.BYBIT_URL, 
                                             params={"category": "spot", 
                                                     "symbol": asset}) as response:
                    if response.status == 200:
                        self._logger.info(f'Recieved response with status {response.status}')
                        try:
                            json_response = await response.json()
                        except ValueError as exc:
                            msg=f'Response is not JSON. Asset:{asset}, request_id:{request_id}'
                            self._logger.error(msg)
                            raise ClientError(msg) from exc
                        
                    elif response.status == 429 or 500 < response.status < 600:
                        if attempt >= self._settings.RETRIES:
                            msg=f'Max retries. Asset:{asset}, request_id:{request_id}'
                            self._logger.error(msg)
                            raise ClientError(msg)
                        else:
                            await asyncio.sleep(0.2 * (2 ** attempt))
                            continue

                    else:
                         msg=f'Bad status {response.status}. Asset:{asset}, request_id:{request_id}'
                         self._logger.error(msg)
                         raise ClientError(msg)
                    
                quote_info = response_validation(json_response, asset, self.provider)
                return quote_info
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                if attempt >= self._settings.RETRIES:
                            msg=f'Max retries. Asset:{asset}, request_id:{request_id}'
                            self._logger.error(msg)
                            raise ClientError(msg) from exc
                else:
                    msg=f'Error: {exc.__class__.__name__}. Asset:{asset}, request_id:{request_id}'
                    self._logger.error(msg)
                    await asyncio.sleep(0.2 * (2 ** attempt))
                    continue
        raise ClientError(f'Unexpected fetch failure. Asset:{asset}, id={request_id}')