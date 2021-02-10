FROM python:3.8.5-buster

ENV AWS_REGION=us-east-1
ENV LOGGING_LEVEL=INFO
ENV ENV=prod
ENV S3_BUCKET=protag-au-twitter

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

CMD ["python", "./app/main.py"]
