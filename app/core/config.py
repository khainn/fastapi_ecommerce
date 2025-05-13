import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent.absolute()
print(f"Loading .env from: {os.path.join(BASE_DIR, '.env')}")
load_dotenv(os.path.join(BASE_DIR, '.env'))
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'FastAPI Ecommerce')
    SECRET_KEY: str = os.getenv('SECRET_KEY', '')
    API_PREFIX: str = os.getenv('API_PREFIX', '/api/v1')
    BACKEND_CORS_ORIGINS: list = ['*']
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # Token expired after 7 days
    SECURITY_ALGORITHM: str = 'HS256'

    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        return self.DATABASE_URL


settings = Settings()
