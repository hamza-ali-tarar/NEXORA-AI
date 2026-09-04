try:
    from importlib import import_module

    _pydantic_settings = import_module("pydantic_settings")
    BaseSettings = _pydantic_settings.BaseSettings
    SettingsConfigDict = _pydantic_settings.SettingsConfigDict
except (ImportError, AttributeError):
    # Support environments that still provide settings through Pydantic v1.
    from pydantic import BaseSettings

    def SettingsConfigDict(**kwargs: object) -> dict[str, object]:
        return kwargs


from typing import Literal

from pydantic import model_validator


class Settings(BaseSettings):
    APP_NAME: str = "NEXORA AI"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "AI-powered Knowledge, Data & Automation Platform"
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./nexora.db"

    AI_PROVIDER: Literal["openai", "mock"] = "openai"
    OPENAI_API_KEY: str | None = None

    SECRET_KEY: str = "dev-secret-key-change-in-production"

    @model_validator(mode="after")
    def validate_production_security(self):
        if self.ENVIRONMENT.lower() == "production":
            if self.SECRET_KEY == "dev-secret-key-change-in-production":
                raise ValueError(
                    "A secure SECRET_KEY is required in production."
                )

            self.DEBUG = False

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()