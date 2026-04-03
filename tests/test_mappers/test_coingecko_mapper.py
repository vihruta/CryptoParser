import pytest
from decimal import Decimal

from src.app.infra.providers.coingecko.mapper import response_validation
from src.app.domain.errors import ValidationError

ASSET = 'BTC'
PROVIDER = 'Coingecko'
COIN_ID = 'bitcoin'
VS_CURRENCY='usd'

def test_coingecko_mapper_happy_path():
    raw_btc = {
        'bitcoin': {
            'usd': 123.45,
            'last_updated_at': 1700000000
        }
    }

    
    result = response_validation(data=raw_btc,asset=ASSET,
                                 vs_currency=VS_CURRENCY, 
                                 coin_id=COIN_ID, 
                                 provider=PROVIDER)
    
    assert result.price == Decimal('123.45')
    assert result.source == 'Coingecko'


def test_coingecko_mapper_negative_price():
    raw_btc = {
        'bitcoin': {
            'usd': -123.45,
            'last_updated_at': 1700000000
        }
    }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,asset=ASSET,
                                 vs_currency=VS_CURRENCY, 
                                 coin_id=COIN_ID, 
                                 provider=PROVIDER)
        

def test_coingecko_mapper_missing_time():
    raw_btc = {
        'bitcoin': {
            'usd': 123.45
        }
    }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,asset=ASSET,
                                 vs_currency=VS_CURRENCY, 
                                 coin_id=COIN_ID, 
                                 provider=PROVIDER)


def test_coingecko_mapper_time_invalid_type():
    raw_btc = {
        'bitcoin': {
            'usd': 123.45,
            'last_updated_at': '1700000000'
        }
    }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,asset=ASSET,
                                 vs_currency=VS_CURRENCY, 
                                 coin_id=COIN_ID, 
                                 provider=PROVIDER)
        

def test_coingecko_mapper_price_invalid_type():
    raw_btc = {
        'bitcoin': {
            'usd': 'abc',
            'last_updated_at': 1700000000
        }
    }

    with pytest.raises(ValidationError):
        response_validation(data=raw_btc,asset=ASSET,
                                 vs_currency=VS_CURRENCY, 
                                 coin_id=COIN_ID, 
                                 provider=PROVIDER)
    

def test_coingecko_mapper_timestamp_seconds():
    raw_btc = {
        'bitcoin': {
            'usd': 123.45,
            'last_updated_at': 1700000000
        }
    }

    result = response_validation(data=raw_btc,asset=ASSET,
                                 vs_currency=VS_CURRENCY, 
                                 coin_id=COIN_ID, 
                                 provider=PROVIDER)
    
    assert result.time.year == 2023


def test_coingecko_mapper_timestamp_milliseconds():
    raw_btc = {
        'bitcoin': {
            'usd': 123.45,
            'last_updated_at': 1700000000000
        }
    }

    result = response_validation(data=raw_btc,asset=ASSET,
                                 vs_currency=VS_CURRENCY, 
                                 coin_id=COIN_ID, 
                                 provider=PROVIDER)
    
    assert result.time.year == 2023