from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ValidationError

from decimal import Decimal
from datetime import datetime, timezone

def response_validation(data: dict, asset: str) -> QuoteInfo:
    if 'symbol' in data and asset in data['symbol']:
        
        if 'closeTime' in data:
            update_time = datetime.fromtimestamp(data['closeTime'] / 1000, 
                                                 tz=timezone.utc)
        else:
            raise ValidationError(f'No definition for time! Asset:{asset}')
        
        if 'lastPrice' in data:
            price = Decimal(str(data['lastPrice']))
        else:
            raise ValidationError(f'No definition for price!. Asset{asset}')
        
        try:
            return QuoteInfo(
                source='binance',
                price=price,
                time=update_time
            )
        except ValidationError as exc:
            raise ValidationError(f'No validation! Asset:{asset}') from exc
        
    else:
        raise ValidationError(f'No data! Asset: {asset}') 
