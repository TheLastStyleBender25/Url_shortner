import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = os.getenv('ENV_FILE', '.env')

class Settings(BaseSettings):
    DB_PORT:int
    DB_USER:str
    DB_NAME:str
    DB_PASSWORD:str
    DB_HOST:str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int

    REDIS_HOST: str
    REDIS_PORT: int

    RESEND_API_KEY: str
    EMAIL_FROM: str

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore')

settings = Settings()