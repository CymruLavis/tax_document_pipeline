from pydantic_settings import BaseSettings, SettingsConfigDict


class GmailConfig(BaseSettings):
    PROVIDER: str = "gmail"
    CLIENT_ID: str
    CLIENT_SECRET: str
    TOKEN_URL: str
    REDIRECT_URI: str
    BASE_URL: str
    AUTH_URL: str
    SCOPES: list[str]
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="GMAIL_"
    )
