from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "presearch-doppelgange-proxy"
    debug: bool = False

    # Replace these with values you capture from browser devtools.
    upstream_text_url: str = "https://example.com/api/text-search"
    upstream_image_url: str = "https://explore.fans/api/presearch/image-search"
    upstream_timeout_seconds: int = 20

    # Optional auth/cookie captured from your session if required by upstream.
    upstream_authorization: str | None = None
    upstream_cookie: str | None = None
    upstream_origin: str | None = "https://presearch.com"
    upstream_referer: str | None = "https://presearch.com/"
    upstream_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    )

    default_mode: str = "spicy"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
