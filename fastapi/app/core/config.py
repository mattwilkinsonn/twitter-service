from pydantic import BaseSettings


class Settings(BaseSettings):

    AWS_REGION: str
    ENV: str
    ES_HOST: str
    SENTRY_DSN: str
    LOGGING_LEVEL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    TWITTER_BEARER_TOKEN: str
    POSTGRES_URL: str

    class Config:
        env_file = ".env"
        env_prefix = ""
        allow_mutation = False
        case_sensitive: True


settings = Settings()