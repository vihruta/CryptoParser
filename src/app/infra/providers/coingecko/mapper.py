from decimal import Decimal
from datetime import datetime, timezone

from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ValidationError

def response_validation(data: dict, asset: str, coin_id: str, vs_currency: str) -> QuoteInfo:
    if coin_id in data:

        if vs_currency in data[coin_id]:
            price = Decimal(data[coin_id][vs_currency])
        else:
            raise ValidationError(f'No definition for price!. Asset{asset}')
        
        if 'last_updated_at' in data[coin_id]:
            updated_time = datetime.fromtimestamp(data[coin_id]['last_updated_at']/1000, 
                                                  tz=timezone.utc)
        else:
            raise ValidationError(f'No definition for time! Asset:{asset}')
        
        try:
            return QuoteInfo(source='coingecko', price=price,
                             time=updated_time)
        except ValidationError as exc:
            raise ValidationError(f'No validation. Asset: {asset}') from exc
        
    else:
        raise ValidationError(f'No data! Asset:{asset}')