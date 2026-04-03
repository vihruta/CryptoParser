import pytest
from decimal import Decimal

from src.app.infra.providers.bybit.mapper import response_validation
from src.app.domain.errors import ValidationError

ASSET = 'BTCUSDT'
PROVIDER = 'Bybit'

def test_bybit_mapper_happy_path():
    raw_btc = {
        'result':
        {
            'list':[{
                    'symbol': 'BTCUSDT',
                    'usdIndexPrice': '123.45'
            }]
        },
        'time': 1499869899040
        }

    result = response_validation(data=raw_btc,
                                 asset=ASSET,
                                 provider=PROVIDER)
    

    assert result.price == Decimal('123.45')
    assert result.source == 'Bybit'


def test_bybit_mapper_negative_price():
    raw_btc = {
        'result':
        {
            'list':[{
                    'symbol': 'BTCUSDT',
                    'usdIndexPrice': '-123.45'
            }]
        },
        'time': 1499869899040
        }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                                    asset=ASSET,
                                    provider=PROVIDER)
        

def test_bybit_mapper_missing_time():
    raw_btc = {
        'result':
        {
            'list':[{
                    'symbol': 'BTCUSDT',
                    'usdIndexPrice': '-123.45'
            }]
        }
        }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                                    asset=ASSET,
                                    provider=PROVIDER)
        
    
def test_bybit_mapper_time_invalid_type():
    raw_btc = {
        'result':
        {
            'list':[{
                    'symbol': 'BTCUSDT',
                    'usdIndexPrice': '123.45'
            }]
        },
        'time': '1499869899040'
        }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                                    asset=ASSET,
                                    provider=PROVIDER)
        

def test_bybit_mapper_price_invalid_type():
    raw_btc = {
        'result':
        {
            'list':[{
                    'symbol': 'BTCUSDT',
                    'usdIndexPrice': 'abs'
            }]
        },
        'time': 1499869899040
        }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,
                                    asset=ASSET,
                                    provider=PROVIDER)
        

def test_bybit_mapper_timestamp_seconds():
    raw_btc = {
        'result':
        {
            'list':[{
                    'symbol': 'BTCUSDT',
                    'usdIndexPrice': '123.45'
            }]
        },
        'time': 1700000000
        }
    
    result = response_validation(data=raw_btc, 
                                 asset=ASSET, 
                                 provider=PROVIDER)
    
    assert result.time.year == 2023


def test_bybit_mapper_timestamp_milliseconds():
    raw_btc = {
        'result':
        {
            'list':[{
                    'symbol': 'BTCUSDT',
                    'usdIndexPrice': '123.45'
            }]
        },
        'time': 1700000000000
        }
    
    result = response_validation(data=raw_btc, 
                                 asset=ASSET, 
                                 provider=PROVIDER)
    
    assert result.time.year == 2023