from app.core.config import Settings


def validate_api_keys(settings: Settings) -> None:
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not found. Please add it to your .env file.")
