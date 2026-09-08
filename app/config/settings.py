from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sentinel_client_id: str | None = None
    sentinel_client_secret: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"
    
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"
    planner_provider: str = "gemini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()