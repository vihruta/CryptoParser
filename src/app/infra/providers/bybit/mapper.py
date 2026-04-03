from decimal import Decimal,InvalidOperation

from datetime import datetime, timezone
from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ValidationError

def response_validation(data: dict, asset: str, provider: str) -> QuoteInfo:
    if 'list' in data['result'] and asset == data['result']['list'][0]['symbol']:
        
        if 'usdIndexPrice' in data['result']['list'][0]:
            try:
                price = Decimal(data['result']['list'][0]['usdIndexPrice'])
                price = price.quantize(Decimal("1.0000"))
            except (TypeError, InvalidOperation):
                raise ValidationError(f'Price is not number.Asset:{asset} Source:{provider}')
        else:
            raise ValidationError(f'No definition for price!. Asset: {asset} Source:{provider}')
        if 'time' in data:
            try:
                if data['time'] > 10**12:
                    update_time = datetime.fromtimestamp(data['time'] / 1000, 
                                                 tz=timezone.utc)
                else:
                    update_time = datetime.fromtimestamp(data['time'], 
                                                 tz=timezone.utc)
            except (TypeError, ValueError) :
                raise ValidationError(f'Time is not number.Asset:{asset} Source:{provider}')
        else:
            raise ValidationError(f'No definition for time! Asset:{asset} Source:{provider}')
        
        return QuoteInfo(source=provider, 
                         price=price,
                         time=update_time)
    else:
        raise ValidationError(f'No data! Asset:{asset} Source:{provider}') 