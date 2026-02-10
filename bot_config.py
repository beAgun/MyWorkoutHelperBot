from pydantic_settings import BaseSettings, SettingsConfigDict
    

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    BOT_TOKEN: str
    WEBHOOK_PATH: str = ''


settings = Settings()
