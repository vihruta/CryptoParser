from typing import Protocol
from src.app.domain.models import Quote, QuoteInfo

class ClientProtocol(Protocol):
    provider: str

    async def fetch_rate(self, asset: str, request_id: str) -> QuoteInfo:
        ...

class StorageProtocol(Protocol):
    async def save_quotes(self, run_id: str, quotes: list[Quote]) -> None:
        ...

