import pytest
from decimal import Decimal

from datetime import datetime, timezone
from src.app.services.collector import Collector
from src.app.domain.models import QuoteInfo, Quote
from src.app.domain.errors import ClientError
from src.app.config import Settings

class FakeClient:
    def __init__(self, responses: dict[str, dict], errors: set[str] = set()):
        self.responses = responses
        self.errors = errors or set()
        self.calls: list[tuple[str, str]] = []
    provider = 'Fake'

    async def fetch_rate(self, asset: str, request_id: str) -> QuoteInfo:
        self.calls.append((asset, request_id))
        if asset in self.errors:
            raise ClientError('boom')
        return QuoteInfo(self.provider, Decimal(str(self.responses[asset]['PRICE'])),
                         datetime.fromtimestamp(self.responses[asset]['LAST_UPDATE_TS'],tz=timezone.utc))

class FakeStorage:
    def __init__(self):
        self.saved = []          # list[Quote]
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
async def test_service_dedup():
    raw_btc = {
        "BTC": {
            "LAST_UPDATE_TS": 1700000000,
            "PRICE": 123.45
            }
    }

    settings = Settings(
        BINANCE_URL='x',
        BYBIT_URL='x',
        COINGECKO_URL='x',
        COINGECKO_APIKEY='x',
        TIMEOUT_SEC=3,
        RETRIES=5,
        FAIL_FAST=False,
        LOG_LEVEL="INFO",
        OUTPUT_PATH="result.txt"
    )

    client = FakeClient(responses=raw_btc)
    storage = FakeStorage()

    collector = Collector(clients=[client], storage=storage, 
                          settings=settings, logger=DummyLogger())
    assets = ["BTC", "btc", "BTC", "bTc"]

    result = await collector.process_assets(assets=assets, run_id='run-1')

    assert len(client.calls) == 1
    assert client.calls[0][0] == 'BTC'
    assert result.total_assets == 1
    assert len(storage.saved) == 1
    assert result.saved_count == 1