from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL : str = "postgresql://postgres:root45#karma@localhost:5432/billing_db"
    SECRET_KEY: str = "0bda582f7f49fec6acd5e6b93f5667cdcb626b116a7ca315d90aad82703c7581"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
