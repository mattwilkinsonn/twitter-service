
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# set path to our python api file
ENV MODULE_NAME="app.main"

# copy contents of project into docker
COPY ./ /app

COPY ./.env.production /app/.env

ENV ES_HOST=vpc-tweets-1-nlghopg6527czyfi4pjue55b3m.us-east-1.es.amazonaws.com



RUN apt-get update
RUN apt-get install -y sudo awscli

# install poetry
RUN pip install poetry

# disable virtualenv for peotry
RUN poetry config virtualenvs.create false

# install dependencies
RUN poetry install