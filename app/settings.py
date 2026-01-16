from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    app_name: str = Field(default="checkfox-api-skillcheck")
    log_level: str = Field(default="INFO")

    bearer_token: str = Field(default="FakeCustomerToken")

    user_id: str = Field(..., min_length=1)
    customer_base_url: str = Field(default="https://contactapi.static.fyi")

    send_to_customer: bool = Field(default=True)
    request_timeout_seconds: float = Field(default=10.0)


settings = Settings()
