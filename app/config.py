from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MPESA_CONSUMER_KEY: str
    MPESA_CONSUMER_SECRET: str
    MPESA_BUSINESS_SHORTCODE: str
    MPESA_PASSKEY: str
    MPESA_CALLBACK_URL: str = "https://3cc8-41-139-239-91.ngrok-free.app/callbacks/mpesa"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()