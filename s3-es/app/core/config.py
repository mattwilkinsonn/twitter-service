from pydantic import BaseSettings


class Settings(BaseSettings):

    AWS_REGION: str
    ENV: str = "local"
    ES_HOST: str
    SENTRY_DSN: str
    LOGGING_LEVEL: str = "INFO"
    S3_BUCKET: str

    class Config:
        env_file = ".env"
        env_prefix = ""
        allow_mutation = False
        case_sensitive: True


settings = Settings()
