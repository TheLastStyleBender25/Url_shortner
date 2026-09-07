from pydantic_settings import BaseSettings, SettingsConfigDict
import os

ENV_FILE = os.getenv('ENV_FILE', '.env')

class Settings(BaseSettings):
    DB_PORT:int
    DB_USER:str
    DB_NAME:str
    DB_PASSWORD:str
    DB_HOST:str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore')

settings = Settings()