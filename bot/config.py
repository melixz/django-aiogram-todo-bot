from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    api_base_url: str = "http://backend:8000/api/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
