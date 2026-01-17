# eskisi:
# from pydantic import BaseSettings

# yenisi:
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool
    openai_api_key: str  

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    class Config:
        env_file = ".env"
        extra = "forbid"
settings = Settings()
