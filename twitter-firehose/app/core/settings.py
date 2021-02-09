from pydantic import BaseSettings


class Settings(BaseSettings):
    # Grabs ENV variables and stores in settings object
    AWS_REGION: str
    ENV: str
    SENTRY_DSN: str
    TWITTER_BEARER_TOKEN: str

    class Config:
        env_file = ".env"
        env_prefix = ""
        allow_mutation = False
        case_sensitive: True


settings = Settings()