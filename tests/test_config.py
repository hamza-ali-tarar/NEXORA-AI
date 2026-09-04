from app.core.config import Settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.APP_NAME == "NEXORA AI"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is True
    assert settings.DATABASE_URL == "sqlite:///./nexora.db"
    assert settings.OPENAI_API_KEY is None


def test_settings_reads_environment_variables(monkeypatch):
    monkeypatch.setenv("APP_NAME", "NEXORA TEST")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    settings = Settings(_env_file=None)

    assert settings.APP_NAME == "NEXORA TEST"
    assert settings.ENVIRONMENT == "testing"
    assert settings.DEBUG is False
    assert settings.SECRET_KEY == "test-secret-key"
    assert settings.OPENAI_API_KEY == "test-api-key"