"""Application configuration loaded from environment variables.

Uses pydantic-settings to validate required environment variables at
startup (fail-fast), instead of failing later when a missing variable
is first accessed.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-based application settings.

    All fields except ENVIRONMENT are required; the application will
    raise a ValidationError and refuse to start if any of them is
    missing from the .env file or the real environment.
    """

    DATABASE_URL: str
    REDIS_URL: str
    GROQ_API_KEY: str
    MCP_SERVER_URL: str
    MCP_API_KEY: str
    GITHUB_TOKEN: str
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"

    ROUTER_MODEL: str = "openai/gpt-oss-20b"
    SPECIALIST_MODEL: str = "openai/gpt-oss-120b"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()