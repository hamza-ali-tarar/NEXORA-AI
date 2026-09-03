from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "NEXORA AI"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "AI-powered Knowledge, Data & Automation Platform"
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
