from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    GROQ_API_KEY: str
    MCP_SERVER_URL: str
    MCP_API_KEY: str
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()