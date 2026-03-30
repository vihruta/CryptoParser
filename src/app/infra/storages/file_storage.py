import aiofiles
from pathlib import Path

from src.app.domain.protocols import StorageProtocol
from src.app.domain.models import Quote
from src.app.domain.errors import StorageError


class FileStorage(StorageProtocol):
    def __init__(self,
                path: Path, 
                logger):
        self._path = path
        self._logger = logger

    async def save_quotes(self, run_id: str, quotes: list[Quote]):
        self._logger.info(f'Writting {len(quotes)} quotes to {self._path}, RUN-ID: {run_id}')
        try:
            async with aiofiles.open(self._path, 'a', encoding='utf-8') as file:
                for quote in quotes:
                    self._logger.info(f'Writting {quote.currency}')
                    await file.write(f"Run-ID: {run_id} Asset: {quote.currency}\n")
                    for info_per_source in quote.info:
                        await file.write(f"Source: {info_per_source.source}, Price: {info_per_source.price}, Time: {info_per_source.time}\n")
                await file.write('\n')
        except OSError as exc:
            msg = 'OS error while saving'
            self._logger.error(msg, run_id=run_id, error=str(exc))
            raise StorageError(msg) from exc
        
                        
