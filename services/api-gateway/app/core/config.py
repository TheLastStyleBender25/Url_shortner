from pydantic_settings import BaseSettings, SettingsConfigDict
import os


ENV_FILE = os.getenv('ENV_FILE', '.env')


class Settings(BaseSettings):
    AUTH_SERVICE_URL: str
    URL_SERVICE_URL: str

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore')

settings = Settings()