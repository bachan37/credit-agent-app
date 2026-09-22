from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Demo Application"
    
    # API URLs
    CREDIT_API_BASE_URL: str = "http://should-set-base-url-in-env/api/v1"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""

    # Automatically load from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate a single settings instance
settings = Settings()