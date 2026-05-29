from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Turkuaz Marketing Parser"
    database_url: str = "sqlite:///./data/marketing_parser.db"
    auto_create_schema: bool = False
    backend_cors_origins: list[str] = ["http://localhost:5174", "http://localhost:5173"]
    backend_cors_origin_regex: str | None = None
    parser_request_timeout: int = 20
    parser_max_retries: int = 3
    parser_request_delay_ms: int = 500
    parser_concurrency: int = 3
    parser_user_agent: str = (
        "Mozilla/5.0 (compatible; MarketingParser/0.1; +https://globus-online.kg)"
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
