from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MPESA_CONSUMER_KEY: str
    MPESA_CONSUMER_SECRET: str
    MPESA_BUSINESS_SHORTCODE: str
    MPESA_PASSKEY: str
    MPESA_CALLBACK_URL: str = "https://yourdomain.com/mpesa-callback"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()