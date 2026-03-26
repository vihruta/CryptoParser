from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ServiceError

from decimal import Decimal
from datetime import datetime, timezone

def response_validation(data: dict, asset: str) -> QuoteInfo:
    if 'symbol' in data and asset in data['symbol']:
        if 'closeTime' in data:
            update_time = datetime.fromtimestamp(data['closeTime'] / 1000, 
                                                 tz=timezone.utc)
        else:
            raise ServiceError('No Time!')
        if 'lastPrice' in data:
            price = Decimal(str(data['lastPrice']))
        else:
            raise ServiceError('No definition for price!')
        try:
            return QuoteInfo(
                source='binance',
                price=price,
                time=update_time
            )
        except ServiceError:
            raise ServiceError('No validation!')
    else:
        raise ServiceError('Dont get any data')
