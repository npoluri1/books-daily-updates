from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Books Daily Updates"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: Optional[str] = None

    smtp_email: Optional[str] = None
    smtp_password: Optional[str] = None

    telegram_bot_token: Optional[str] = None

    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None

    hf_token: Optional[str] = None
    openrouter_key: Optional[str] = None

    notification_time: str = "08:30"
    timezone: str = "Asia/Kolkata"
    max_chapters_per_day: int = 1

    default_currency: str = "USD"
    supported_currencies: str = "USD,EUR,GBP,INR,AED,SGD,AUD,CAD,JPY"
    shipping_weight_unit: str = "kg"
    default_country: str = "US"

    stripe_key: Optional[str] = None
    paypal_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
