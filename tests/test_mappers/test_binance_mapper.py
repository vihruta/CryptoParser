import pytest
from decimal import Decimal

from src.app.infra.providers.binance.mapper import response_validation
from src.app.domain.errors import ValidationError

ASSET = 'BTCUSDT'
PROVIDER = 'Binance'

def test_binance_mapper_happy_path():
    raw_btc = {
        'symbol': 'BTCUSDT',
        'closeTime': 1499869899040,
        'lastPrice': '123.45'
        }

    result = response_validation(data=raw_btc,
                                 asset=ASSET,
                                 provider=PROVIDER)
    

    assert result.price == Decimal(raw_btc['lastPrice'])
    assert result.source == 'Binance'

def test_binance_mapper_negative_price():
    raw_btc = {
        'symbol': 'BTCUSDT',
        'closeTime': 1499869899040,
        'lastPrice': '-123.45'
        }
    
    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                            asset=ASSET,
                            provider=PROVIDER)
        

def test_binance_mapper_missing_close_time():
    raw_btc = {
        'symbol': 'BTCUSDT',
        'lastPrice': '123.45'
        }
    
    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                            asset=ASSET,
                            provider=PROVIDER)
    

def test_binance_mapper_time_invalid_type():
    raw_btc = {
        'symbol': 'BTCUSDT',
        'closeTime': '1499869899040',
        'lastPrice': '123.45'
        }
    
    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                            asset=ASSET,
                            provider=PROVIDER)


def test_binance_mapper_price_invalid_type():
    raw_btc = {
        'symbol': 'BTCUSDT',
        'closeTime': 1499869899040,
        'lastPrice': 'asb'
        }
    
    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                            asset=ASSET,
                            provider=PROVIDER)
        
        
def test_binance_mapper_timestamp_seconds():
    raw_btc = {
        'symbol': 'BTCUSDT',
        'closeTime': 1700000000,
        'lastPrice': '123.45'
        }


    result = response_validation(data=raw_btc,
                                 asset=ASSET,
                                 provider=PROVIDER)
    
    assert result.time.year == 2023


def test_binance_mapper_timestamp_milliseconds():
    raw_btc = {
        'symbol': 'BTCUSDT',
        'closeTime': 1700000000000,
        'lastPrice': '123.45'
        }


    result = response_validation(data=raw_btc,
                                 asset=ASSET,
                                 provider=PROVIDER)
    
    assert result.time.year == 2023