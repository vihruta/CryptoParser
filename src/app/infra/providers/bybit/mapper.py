from decimal import Decimal
from datetime import datetime, timezone
from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ServiceError

def response_validation(data: dict, asset: str) -> QuoteInfo:
    if 'list' in data['result'] and asset in data['result']['list'][0]['symbol']:
        if 'lastPrice' in data['result']['list'][0]:
            price = Decimal(data['result']['list'][0]['lastPrice'])
        else:
            raise ServiceError('No definition for price!')
        if 'time' in data:
            update_time = datetime.fromtimestamp(data['time'] / 1000, 
                                                 tz=timezone.utc)
        else:
            raise ServiceError('No definition for time!')
        try:
            return QuoteInfo(source='bybit', 
                             price=price,
                             time=update_time)
        except ServiceError:
            raise ServiceError('No validation!')

    else:
        raise ServiceError('No data!') 