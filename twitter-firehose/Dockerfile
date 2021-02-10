FROM python:3.8.5-buster

ENV AWS_REGION=us-east-1
ENV ENV=prod

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
