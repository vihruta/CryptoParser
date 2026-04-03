import sys
import aiohttp
from loguru import logger
import uuid
import asyncio
import argparse

from src.app.config import load_setting
from src.app.infra.providers.binance.client import BinanceClient
from src.app.infra.providers.bybit.client import BybitClient
from src.app.infra.providers.coingecko.client import CoinGeckoClient
from src.app.infra.storages.file_storage import FileStorage 
from src.app.services.collector import Collector
from src.app.domain.errors import ConfigError, ClientError, ServiceError, StorageError, ValidationError


def parse_args():
    parser = argparse.ArgumentParser(description='Crypto rates collector')

    parser.add_argument('--assets', dest='assets', nargs='+', required=True, help='Crypto assets like BTC, ETH...')

    return parser.parse_args()

async def main():
    settings = load_setting()
    args = parse_args()
    currencies = args.assets

    timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT_SEC)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        clients = [BinanceClient(session=session, settings=settings,logger=logger),
                    BybitClient(session=session, settings=settings,logger=logger),
                    CoinGeckoClient(session=session, settings=settings,logger=logger)]
        storage = FileStorage(path=settings.OUTPUT_PATH, logger=logger)
        collector = Collector(clients=clients, storage=storage, 
                                settings=settings, logger=logger)
        run_id = str(uuid.uuid4())
        try:
            result = await collector.process_assets(assets=currencies, 
                                                    run_id=run_id)
            logger.info(f'Saved count: {result.saved_count} Error count: {result.errors_count}')
            
            for error in result.errors:
                logger.info(f'''Source: {error.source} Asset: {error.asset}
                            Error type: {error.error_type}. Error msg: {error.error_msg}''')
        except (ConfigError, ClientError, ServiceError, StorageError, ValidationError) as exc:
            logger.error('Error {}', exc)
            return 1
        except Exception as exc:
            logger.error('Error {}', exc)
            return 1
        if result.errors_count > 0:
            return 1
        return 0
    

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))