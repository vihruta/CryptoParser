import pytest

from src.app.services.collector import Collector
from src.app.config import Settings
from src.app.domain.models import Quote, QuoteInfo
from src.app.domain.errors import ClientError,ServiceError,ValidationError

class FakeClient:
    def __init__(self, responses: dict[str, dict], errors: set[str] = set()):
        self.responses = responses
        self.errors = errors
        self.calls: list[tuple[str, str]] = []

    async def fetch_rate(self, asset: str, request_id: str) -> dict:
        self.calls.append((asset, request_id))
        if asset in self.errors:
            raise ClientError("boom")
        return self.responses[asset]
    

class FakeStorage:
    def __init__(self):
        self.saved = []
        self.saved_run_id = None
        self.calls = 0

    async def save_quotes(self, run_id: str, quotes: list[Quote]) -> None:
        self.calls += 1
        self.saved_run_id = run_id
        self.saved = quotes


class DummyLogger:
    def error(self, *args, **kwargs): ...
    def info(self, *args, **kwargs): ...


@pytest.mark.asyncio
async def test_client_negative_price():
    raw_btc = {
        "source": "binance", 
        'price': -123.45,
        'closeTime': 1700000000
    }

    client = FakeClient(responses={'BTC': raw_btc})
    storage = FakeStorage()

    settings = Settings(
        BINANCE_URL='x',
        BYBIT_URL='x',
        COINGECKO_URL='x',
        COINGECKO_APIKEY='x',
        TIMEOUT_SEC=3,
        RETRIES=5,
        FAIL_FAST=0,
        LOG_LEVEL="INFO",
        OUTPUT_PATH="result.txt",
    )

    collector = Collector(clients=[client], 
                          storage=storage, 
                          settings=settings, 
                          logger=DummyLogger())
    assets = ['BTC']
    with pytest.raises(ValidationError):
        await collector.process_assets(assets=assets, run_id='run-1')