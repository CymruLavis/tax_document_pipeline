from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: str
    TOKEN_URL: str
    REDIRECT_URI: str
    PROVIDER: str
    BASE_URL: str
    AUTH_URL: str
    SCOPES: list[str]


class GmailConfig(BaseConfig):
    PROVIDER: str = "gmail"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="GMAIL_"
    )


class OutlookConfig(BaseConfig):
    PROVIDER: str = "outlook"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="OUTLOOK_"
    )
