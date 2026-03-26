"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central settings object populated from the environment or .env file.

    Attributes:
        DATABASE_URL: SQLAlchemy-compatible PostgreSQL connection string.
        SMTP_HOST: Outgoing mail server hostname.
        SMTP_PORT: Outgoing mail server port (typically 587 for STARTTLS).
        SMTP_USER: SMTP authentication username.
        SMTP_PASSWORD: SMTP authentication password or app-specific password.
        SMTP_FROM: Sender address shown in outgoing alert emails.
        CHECK_INTERVAL_HOURS: How often the scheduler checks all product prices.
    """

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pricedb"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    CHECK_INTERVAL_HOURS: int = 6

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Returns:
        A fully populated Settings instance.
    """
    return Settings()
