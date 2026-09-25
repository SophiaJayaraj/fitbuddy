import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


@dataclass(frozen=True)
class Settings:

    # Gemini
    google_api_key: str = os.getenv(
        "GOOGLE_API_KEY",
        ""
    ).strip()

    workout_model: str = os.getenv(
        "GEMINI_WORKOUT_MODEL",
        "gemini-2.5-pro"
    ).strip()

    fast_model: str = os.getenv(
        "GEMINI_FAST_MODEL",
        "gemini-2.5-flash"
    ).strip()

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'fitbuddy.db').as_posix()}",
    ).strip()

    # Demo mode
    demo_mode: bool = _as_bool(
        os.getenv("DEMO_MODE"),
        False
    )

    # Optional admin token
    admin_token: str = os.getenv(
        "ADMIN_TOKEN",
        ""
    ).strip()


settings = Settings()