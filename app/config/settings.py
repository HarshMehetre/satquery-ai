from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sentinel_client_id: str | None = None
    sentinel_client_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()