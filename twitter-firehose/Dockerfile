FROM python:3.8.5-buster

ENV AWS_REGION=us-east-1
ENV ENV=prod
ENV SENTRY_DSN=https://0815e2e14f1f40759b46be465942634f@o127707.ingest.sentry.io/5431348
ENV TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAPDgIwEAAAAAUjUUzx4WdxKWEXE0pTjcKZibeq4%3D8lqY7iQtHvmea3OpzNeK0LukS6HDGlTuWzUlKjOvwZfnR3GDmw

RUN apt-get update
RUN apt-get install -y sudo awscli

# copy contents of project into docker
COPY ./ /app

WORKDIR /app

# install poetry
RUN pip install poetry

# disable virtualenv for poetry
RUN poetry config virtualenvs.create false

# install dependencies
RUN poetry install

CMD ["python", "./app/stream.py"]