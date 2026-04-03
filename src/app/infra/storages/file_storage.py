import aiofiles
import json
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
        self._logger.info(f'Writing {len(quotes)} quotes to {self._path}, RUN-ID: {run_id}')
        try:
            async with aiofiles.open(self._path, 'a', encoding='utf-8') as file:
                for quote in quotes:
                    self._logger.info(f'Writting {quote.currency}')
                    for info_per_source in quote.info:
                        line = json.dumps({
                            "asset": quote.currency,
                            "price": str(info_per_source.price),
                            "source": info_per_source.source,
                            "time": str(info_per_source.time),
                            'run-id': run_id
                        })
                        await file.write(line + '\n')
        except OSError as exc:
            msg = 'OS error while saving'
            self._logger.error(msg, run_id=run_id, error=str(exc))
            raise StorageError(msg) from exc
        
                        
