from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ValidationError

from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone


def response_validation(data: dict, asset: str, provider: str) -> QuoteInfo:
    if 'symbol' in data and asset == data['symbol']:
        
        if 'lastPrice' in data:
            try:
                price = Decimal(str(data['lastPrice']))
                price = price.quantize(Decimal("1.0000"))
            except (TypeError, InvalidOperation):
                raise ValidationError(f'Price is not string.Asset:{asset} Source:{provider}')
        else:
            raise ValidationError(f'No definition for price!. Asset:{asset} Source:{provider}')
        
        if 'closeTime' in data:
            try:
                if data['closeTime'] > 10**12:
                    update_time = datetime.fromtimestamp(data['closeTime'] / 1000, 
                                                        tz=timezone.utc)
                else:
                    update_time = datetime.fromtimestamp(data['closeTime'], 
                                                        tz=timezone.utc)
            except (TypeError, ValueError):
                raise ValidationError(f'Time is not number.Asset:{asset} Source:{provider}')
        else:
            raise ValidationError(f'No definition for time! Asset:{asset} Source:{provider}')
        
        return QuoteInfo(
            source=provider,
            price=price,
            time=update_time
            )
        
    else:
        raise ValidationError(f'No data! Asset: {asset} Source:{provider}') 
