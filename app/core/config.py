"""Core application configuration.

This module handles loading environment variables and constructing database 
connection URLs using Pydantic Settings.
"""

import logging
import os
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings model using Pydantic.

    Loads values from .env file or environment variables.

    Attributes:
        API_V1_STR: The base prefix for version 1 of the API.
        PROJECT_NAME: The name of the project.
        VERSION: The current version of the application.
        POSTGRES_SERVER: The hostname or IP address of the PostgreSQL server.
        POSTGRES_USER: The username for PostgreSQL authentication.
        POSTGRES_PASSWORD: The password for PostgreSQL authentication.
        POSTGRES_DB: The name of the PostgreSQL database.
    """
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "fps database"
    VERSION: str = "0.1.0"
    
    # Database configuration
    POSTGRES_SERVER: str = "server"
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "db"
    
    # API authentication
    API_KEY_TEAM_A: str = "897c4fe2-c144-4021-84a8-564f41a183d9"
    API_KEY_TEAM_B: str = "d2656787-32a6-45b8-b64d-e781a200e737"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

    @property
    def database_url(self) -> str:
        """Dynamically constructs the PostgreSQL connection string.

        Safely URL-encodes the password to handle special characters.

        Returns:
            str: The fully qualified PostgreSQL connection URL.

        Raises:
            Exception: If there is an error during URL construction.
        """
        try:
            import urllib.parse
            encoded_password = urllib.parse.quote_plus(self.POSTGRES_PASSWORD)
            return f"postgresql://{self.POSTGRES_USER}:{encoded_password}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        except Exception as e:
            logger.error(f"Error constructing database URL: {e}")
            raise

try:
    settings = Settings()
except Exception as e:
    # Use a basic print here as logging might not be fully configured yet if this fails early
    print(f"CRITICAL: Failed to load application settings: {e}")
    raise
