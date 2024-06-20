import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

ENV: str = ""


class Configs(BaseSettings):
    # base
    ENV: str = os.getenv("ENV", "dev")
    API: str = "/api"
    ENV_DATABASE_MAPPER: dict = {
        "dev": "memes",
    }

    DB_ENGINE: str = "postgresql+asyncpg"

    PROJECT_ROOT: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # database
    DB_NAME: str = os.getenv("POSTGRES_DB")
    DB_USER: str = os.getenv("POSTGRES_USER")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    DATABASE_URI_FORMAT: str = "{db_engine}://{user}:{password}@{host}/{database}"

    DATABASE_URI: str = "{db_engine}://{user}:{password}@{host}/{database}".format(
        db_engine=DB_ENGINE,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=ENV_DATABASE_MAPPER[ENV],
    )

    class Config:
        case_sensitive = True


configs = Configs()
