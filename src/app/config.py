from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.app.domain.errors import ConfigError, ValidationError


class Settings(BaseSettings):
    BINANCE_URL: str
    BYBIT_URL: str
    COINGECKO_URL: str
    COINGECKO_APIKEY: str
    TIMEOUT_SEC: int
    RETRIES: int
    FAIL_FAST: bool
    LOG_LEVEL: str
    OUTPUT_PATH: Path

    @field_validator("OUTPUT_PATH", mode="before")
    @classmethod
    def normalize_result_path(cls, value: Any) -> Path:
        if isinstance(value, str):
            path = Path(value)
            if path.is_absolute():
                return path
            base_dir = Path(__file__).resolve().parent.parent.parent
            return base_dir / path
        if isinstance(value, Path):
            return value
        raise ConfigError('Invalid OUTPUT_PATH')
    
    @field_validator("TIMEOUT_SEC")
    @classmethod
    def validate_timeout(cls, value: int) -> int:
        if value < 0:
            raise ConfigError('TIMEOUT_SEC must be positive!')
        return value
    
    @field_validator("RETRIES")
    @classmethod
    def validate_retries(cls, value: int) -> int:
        if value < 1:
            raise ConfigError('RETRIES must be > 1')
        return value
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

def load_setting() -> Settings:
    try:
        return Settings() # type: ignore[call-arg]
    except ValidationError as exc:
        raise ConfigError(f'Invalid configrutation {exc}') from exc