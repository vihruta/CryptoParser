import aiohttp
import asyncio

from src.app.domain.protocols import ClientProtocol
from src.app.config import Settings
from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ClientError
from src.app.infra.providers.coingecko.mapper import response_validation

COINGECKO_ASSET_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "USDC": "usd-coin",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "TRX": "tron",
    "TON": "the-open-network",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "LINK": "chainlink",
    "XLM": "stellar",
    "ATOM": "cosmos",
    "ETC": "ethereum-classic",
    "FIL": "filecoin",
    "ICP": "internet-computer",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "NEAR": "near",
    "XMR": "monero", 
}

class CoinGeckoClient(ClientProtocol):
    def __init__(self, session,
               settings: Settings,
               logger):
        self._session = session
        self._settings = settings
        self._logger = logger
        self.provider = 'Coingecko'
        
    async def fetch_rate(self, asset, request_id) -> QuoteInfo:
        vs_currency = 'usd'
        try:
            coin_id = COINGECKO_ASSET_MAP[asset]
            for attempt in range(1, self._settings.RETRIES + 1):
                self._logger.info(f'Asset={asset}, id={request_id}, attempt={attempt}')
                try:
                    headers = {"x-cg-demo-api-key": self._settings.COINGECKO_APIKEY}
                    params = {"vs_currencies": vs_currency,"ids": coin_id, "include_last_updated_at": "true"}
                    async with self._session.get(self._settings.COINGECKO_URL, 
                                                 headers=headers, params=params) as response:
                        if response.status == 200:
                            self._logger.info(f'Recieved response with status {response.status}')
                            try:
                                json_response = await response.json()
                            except ValueError as exc:
                                msg = f'Response in not JSON. Asset:{asset}, request_id: {request_id}'
                                self._logger.error(msg)
                                raise ClientError(msg) from exc
                        elif response.status == 429 or 500 < response.status < 600:
                            if attempt >= self._settings.RETRIES:
                                msg = f'Max retries. Asset:{asset}, request_id: {request_id}'
                                self._logger.error(msg)
                                raise ClientError(msg)
                            else:
                                await asyncio.sleep(0.2 * (2 ** attempt))
                                msg = f'''Bad status: {response.status}.Retry. 
                                Asset: {asset}, request_id:{request_id}'''
                                continue
                        else:
                            msg = f'Bad status: {response.status}. Asset: {asset}, request_id:{request_id}'
                            self._logger.error(msg)
                            raise ClientError(msg)
                        
                        qoute_info = response_validation(json_response, asset, coin_id, vs_currency, self.provider)
                        return qoute_info
                    
                except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                    if attempt >= self._settings.RETRIES:
                        msg = f'Max retries. Asset:{asset}, request_id: {request_id}'
                        self._logger.error(msg)
                        raise ClientError(msg) from exc
                    else:
                        await asyncio.sleep(0.2 * (2 ** attempt))
                        continue

        except KeyError as exc:
            msg = f'No asset in asset map. Asset: {asset}. Request id:{request_id}'
            self._logger.error(msg)
            raise ClientError(msg) from exc
        raise ClientError(f'Unexpected fetch failure. Asset={asset}, id={request_id}')