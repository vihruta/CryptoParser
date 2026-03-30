from src.app.domain.models import QuoteInfo
from src.app.domain.errors import ValidationError

from decimal import Decimal
from datetime import datetime, timezone

def response_validation(data: dict, asset: str, provider: str) -> QuoteInfo:
    if 'symbol' in data and asset in data['symbol']:
        
        if 'closeTime' in data:
            update_time = datetime.fromtimestamp(data['closeTime'] / 1000, 
                                                 tz=timezone.utc)
        else:
            raise ValidationError(f'No definition for time! Asset:{asset} Source: {provider}')
        
        if 'lastPrice' in data:
            price = Decimal(str(data['lastPrice']))
            price = price.quantize(Decimal("1.0000"))
        else:
            raise ValidationError(f'No definition for price!. Asset{asset} Source: {provider}')
        
        try:
            return QuoteInfo(
                source=provider,
                price=price,
                time=update_time
            )
        except ValidationError as exc:
            raise ValidationError(f'No validation! Asset:{asset} Source: {provider}') from exc
        
    else:
        raise ValidationError(f'No data! Asset: {asset} Source: {provider}') 
