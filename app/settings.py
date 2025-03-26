import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    API_PREFIX: str = "/api/v1"

    PROJECT_NAME: str = "Tic Tac Toe Online"
    PROJECT_VERSION: str = "0.0.5"
    DEBUG: bool = os.getenv("DEBUG", False)

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOSTNAME: str = "localhost"  # TODO: return os.getenv("POSTGRES_HOSTNAME", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tic_tac_toe")
    DATABASE_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: str = os.getenv("REDIS_PORT", 6379)
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    REDIS_CHANNEL: str = os.getenv("REDIS_CHANNEL", "game_cache")

    SECRET: str = os.getenv("SECRET_KEY", uuid4().hex)
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE: int = int(os.getenv("ACCESS_TOKEN_EXPIRE", 3600))


settings = Settings()
