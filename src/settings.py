import os
from importlib.metadata import version
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    SERVICE_TITLE: str = "agenda-service"
    SERVICE_DESCRIPTION: str = "An API meant as a sort of 'facade' for the google agenda."
    SERVICE_VERSION: str = os.getenv("SERVICE_VERSION", "0.1.0")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = os.getenv("PORT", 8080)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    ACCESS_TOKEN_COOKIE_NAME: str = os.getenv("ACCESS_TOKEN_COOKIE_NAME", "access_token")
    KEYCLOAK_PUBLIC_KEY: Optional[str] = os.getenv("KEYCLOAK_PUBLIC_KEY")
    JWT_VALIDATION_ENABLED: bool = os.getenv("JWT_VALIDATION_ENABLED", True)

settings = Settings()
