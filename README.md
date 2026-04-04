# Crypto Rates Collector

Асинхронный сервис для сбора цен криптовалют из нескольких источников
(Binance, Bybit, CoinGecko) с нормализацией данных и сохранением результата.

## Features
- параллельные запросы (async + semaphore)
- retry для сетевых ошибок
- timeout на каждый запрос
- нормализация данных к единой модели
- логирование
- сохранение результата в файл (JSON lines)

## Stack

- Python 3.12+
- aiohttp — HTTP клиент
- asyncio — Асинхронность
- pydantic-settings — Конфигурация из переменных
- loguru — логи
- pytest — тестирование

## Installation
```bash
git clone https://github.com/vihruta/CryptoParser
cd CryptoParser

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

## Configuration

Создайте `.env` файл на основе `.env.example`.

Пример:
```env
BINANCE_URL=https://api.binance.com/api/v3/ticker/24hr
BYBIT_URL=https://api-testnet.bybit.com/v5/market/tickers
COINGECKO_URL=https://api.coingecko.com/api/v3/simple/price
COINGECKO_APIKEY=
TIMEOUT_SEC=3        # timeout одного запроса
CONCURRENCY=5        # максимальное количество одновременных запросов
RETRIES=5            # количество повторных попыток
FAIL_FAST=0          # остановить выполнение при первой ошибке (1/0)
OUTPUT_PATH=result.jsonl
```

## Usage

```bash
python -m app --assets BTC ETH SOL
# или
python -m app --assets btc eth sol
```

## Architecture

- Client - получение данных из API
- Mapper - преобразование ответа API во внутреннюю модель
- Collector - бизнес-логика и оркестрация
- Storage - сохранение результатов
- Models - доменные модели
- Errors - исключения
- Protocols - абстракции классов

## Tests

```bash
pytest
```
Example:
```bash
collected 30 items
30 passed in 0.11s
```

### Results
Программа выводит статистику выполнения и сохраняет результат в файл OUTPUT_PATH.
Example output:
```json
{"asset": "BTC", "price": "66862.9400", "source": "Binance", "time": "2026-04-03 23:13:44.001000+00:00", "run-id": "34d02758-539c-46d9-8a5b-d96a0a7ff15e"}
{"asset": "BTC", "price": "66855.7711", "source": "Bybit", "time": "2026-04-03 23:13:44.494000+00:00", "run-id": "34d02758-539c-46d9-8a5b-d96a0a7ff15e"}
{"asset": "BTC", "price": "66878.0000", "source": "Coingecko", "time": "2026-04-03 23:13:22+00:00", "run-id": "34d02758-539c-46d9-8a5b-d96a0a7ff15e"}
```

### Error Handling
- Network errors → ретрай
- Validation errors → не ретраятся
- FAIL_FAST=True → выполнение останавливается при первой ошибке
