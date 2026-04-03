from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone

from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ValidationError

def response_validation(data: dict, asset: str, coin_id: str, vs_currency: str, provider: str) -> QuoteInfo:
    if coin_id in data:

        if vs_currency in data[coin_id]:
            try:
                price = Decimal(data[coin_id][vs_currency])
                price = price.quantize(Decimal("1.0000"))
            except (TypeError, InvalidOperation):
                raise ValidationError(f'Price is not number.Asset:{asset} Source:{provider}')
        else:
            raise ValidationError(f'No definition for price!. Asset:{asset} Source:{provider}')
        
        if 'last_updated_at' in data[coin_id]:
            try:
                if data[coin_id]['last_updated_at'] > 10**12:
                    updated_time = datetime.fromtimestamp(data[coin_id]['last_updated_at']/1000, 
                                                          tz=timezone.utc)
                else:
                    updated_time = datetime.fromtimestamp(data[coin_id]['last_updated_at'], 
                                                          tz=timezone.utc)
            except (TypeError, ValueError) :
                raise ValidationError(f'Time is not number. Asset:{asset} Source:{provider}')
        else:
            raise ValidationError(f'No definition for time! Asset:{asset} Source:{provider}')
        
        return QuoteInfo(source=provider, 
                         price=price,
                         time=updated_time)
        
    else:
        raise ValidationError(f'No data! Asset:{asset} Source:{provider}')