from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from src.app.domain.errors import ServiceError, ValidationError


@dataclass
class QuoteInfo:
    source: str
    price: Decimal
    time: datetime

    def __post__init__(self):
        if((self.source) is None):
            raise ValidationError('No source of information')
        if self.price < 0:
            raise ValidationError('Price must be positive!')
        
        if self.time.tzinfo is None:
            raise ValidationError('Time must be timezone-aware')
        elif self.time.tzinfo != timezone.utc:
            self.time = self.time.astimezone(timezone.utc)


@dataclass
class Quote:
    currency: str
    info: list[QuoteInfo]

    def __post__init__(self):
        if ((self.currency is None) or 
        (self.currency.strip() == '')):
            raise ValidationError('No asset!')
        if len(self.info) == 0:
            raise ValidationError('No info from exchange!')

@dataclass
class ErrorItem:
    asset: str
    source: str
    error_type: str
    error_msg:str

@dataclass
class ServiceResult:
    run_id: str
    total_assets: int
    saved_count: int
    errors: list[ErrorItem]

    @property
    def errors_count(self) -> int:
        return(len(self.errors))