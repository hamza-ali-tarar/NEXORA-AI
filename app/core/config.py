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


class Settings(BaseSettings):
    APP_NAME: str = "NEXORA AI"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "AI-powered Knowledge, Data & Automation Platform"
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./nexora.db"

    OPENAI_API_KEY: str | None = None

    SECRET_KEY: str = "dev-secret-key-change-in-production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()