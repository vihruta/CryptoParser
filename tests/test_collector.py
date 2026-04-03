import pytest
from decimal import Decimal
from pathlib import Path

from datetime import datetime, timezone
from src.app.services.collector import Collector
from src.app.domain.models import QuoteInfo, Quote
from src.app.domain.errors import ClientError
from src.app.config import Settings

class FakeClient:
    def __init__(self, responses: dict[str, dict], errors: set[str] | None = None):
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

@pytest.fixture
def raw_btc() -> dict[str, dict]:
    return {
            "BTC": {
                "LAST_UPDATE_TS": 1700000000,
                "PRICE": 123.45
            }
    }

@pytest.fixture
def settings() -> Settings:
    return Settings(
        BINANCE_URL='x',
        BYBIT_URL='x',
        COINGECKO_URL='x',
        COINGECKO_APIKEY='x',
        TIMEOUT_SEC=3,
        RETRIES=5,
        FAIL_FAST=False,
        LOG_LEVEL="INFO",
        OUTPUT_PATH=Path("result.txt")
    )

@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def logger() -> DummyLogger:
    return DummyLogger()

@pytest.fixture
def make_collector(settings, logger):
    def _make(clients, storage=None):
        storage = storage or FakeStorage()
        collector = Collector(
            clients=clients,
            storage=storage,
            settings=settings,
            logger=logger)
        return collector, storage
    
    return _make


@pytest.mark.asyncio
async def test_service_dedup(raw_btc, make_collector):
    client = FakeClient(responses=raw_btc)
    collector, storage = make_collector(clients=[client])

    assets = ["BTC",'',' ', "btc", "BTC", "bTc"]

    result = await collector.process_assets(assets=assets, run_id='run-1')

    assert result.total_assets == 1
    assert result.saved_count == 1

    assert len(client.calls) == 1
    assert client.calls[0][0] == 'BTC'

    assert storage.calls == 1
    assert len(storage.saved) == 1
    assert storage.saved[0].currency == 'BTC'


def test_normalize_assets(raw_btc, make_collector):
    client = FakeClient(responses=raw_btc)
    collector, storage = make_collector(clients=[client])

    assets = ["BTC",'',' ', "btc", "BTC", "bTc", 'Eth', 'EtH']

    result = collector.normalize_assets(assets)

    assert len(result) == 2
    assert result == ['BTC', 'ETH']

@pytest.mark.asyncio
async def test_collector_negative_price(make_collector):
    raw_btc = {
            "BTC": {
                "LAST_UPDATE_TS": 1700000000,
                "PRICE": -123.45
            }
    }

    client = FakeClient(responses=raw_btc)
    collector, storage = make_collector(clients=[client])
    assets = ['BTC']

    result = await collector.process_assets(assets=assets, run_id='run-1')

    assert result.total_assets == 1
    assert result.errors_count == 1
    assert result.errors[0].error_type == 'ValidationError'
    assert result.saved_count == 0

    assert len(client.calls) == 1
    assert client.calls[0][0] == 'BTC'

    assert storage.calls == 0
    assert storage.saved == []


@pytest.mark.asyncio
async def test_process_assets_happy_path(raw_btc, make_collector):
    client = FakeClient(responses=raw_btc)
    collector, storage = make_collector(clients=[client])

    assets = ['BTC']

    result = await collector.process_assets(assets=assets, run_id='run-1')

    assert result.errors == []
    assert result.saved_count == 1
    assert result.total_assets == 1

    assert len(client.calls) == 1
    assert client.calls[0][0] == 'BTC'

    assert storage.calls == 1
    assert storage.saved[0].currency == 'BTC'
    assert len(storage.saved) == 1
    assert storage.saved_run_id == 'run-1'


@pytest.mark.asyncio
async def test_two_clients_process_assets(raw_btc, make_collector):
    client_1 = FakeClient(responses=raw_btc)
    client_2 = FakeClient(responses=raw_btc)
    collector, storage = make_collector(clients=[client_1, client_2])

    
    assets = ['BTC']
    result = await collector.process_assets(assets=assets, run_id='run-1')

    assert result.saved_count == 2
    assert result.errors == []
    
    assert len(client_1.calls) == 1
    assert len(client_2.calls) == 1
    assert client_1.calls[0][0] == 'BTC'
    assert client_2.calls[0][0] == 'BTC'

    assert len(storage.saved) == 1
    assert storage.calls == 1
    assert len(storage.saved[0].info) == 2


@pytest.mark.asyncio
async def test_partial_success_process_assets(raw_btc, make_collector):
    client_1 = FakeClient(responses=raw_btc, errors={'BTC'})
    client_2 = FakeClient(responses=raw_btc)
    collector, storage = make_collector(clients=[client_1, client_2])
    
    assets = ['BTC']
    result = await collector.process_assets(assets=assets,run_id='run-1')

    assert result.saved_count == 1
    assert result.errors_count == 1
    assert result.errors[0].error_type == 'ClientError'

    assert len(client_1.calls) == 1
    assert len(client_2.calls) == 1

    assert len(storage.saved) == 1
    assert storage.calls == 1


@pytest.mark.asyncio
async def test_all_clients_are_down(raw_btc, make_collector):
    client_1 = FakeClient(responses=raw_btc, errors={'BTC'})
    client_2 = FakeClient(responses=raw_btc, errors={'BTC'})
    collector, storage = make_collector(clients=[client_1, client_2])
    
    assets = ['BTC']
    result = await collector.process_assets(assets=assets,run_id='run-1')

    assert result.saved_count == 0
    assert result.errors_count == 2
    
    assert storage.calls == 0
    assert len(storage.saved) == 0

@pytest.mark.asyncio
async def test_fail_fast_true_raise_clienterror(raw_btc):
    settings = Settings(
            BINANCE_URL='x',
            BYBIT_URL='x',
            COINGECKO_URL='x',
            COINGECKO_APIKEY='x',
            TIMEOUT_SEC=3,
            RETRIES=5,
            FAIL_FAST=True,
            LOG_LEVEL="INFO",
            OUTPUT_PATH=Path("result.txt")
        )

    client = FakeClient(responses=raw_btc, errors={'BTC'})
    storage = FakeStorage()
    collector = Collector(clients=[client], storage=storage, 
                          settings=settings, logger=DummyLogger())

    assets = ['BTC']

    with pytest.raises(ClientError):
        await collector.process_assets(assets=assets, run_id='run-1')
    
    assert len(client.calls) == 1
    assert client.calls[0][0] == 'BTC'

    assert storage.calls == 0

@pytest.mark.asyncio
async def test_collector_empty_input(raw_btc, make_collector):
    client = FakeClient(responses=raw_btc)
    
    collector, storage = make_collector(clients=[client])

    assets = []
    with pytest.raises(ClientError):
        await collector.process_assets(assets=assets, run_id='run-1')
