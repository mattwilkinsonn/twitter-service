# app.py
from app.twitter.tweet_fetch import tweet_update
from starlette.responses import Response
from app.auth.jwt import (
    OAuth2PasswordBearerWithCookie,
    create_access_token,
    get_current_user,
)
from app.db.schemas import User
from app.db.crud import authenticate_user, get_user, get_user_by_email
from elasticsearch_dsl.aggs import A
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
import logging
import sentry_sdk
from sqlalchemy.orm import Session
from .db.database import engine, get_db
from .db import models, schemas, crud
from .core.config import settings
from .es.es_init import get_es
from elasticsearch_dsl import Search
from pydantic import BaseModel
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
import pprint


# Log messages for debugging based on Logging level ENV variable
if settings.LOGGING_LEVEL == "INFO":
    logging.basicConfig(level=logging.INFO)
if settings.LOGGING_LEVEL == "WARNING":
    logging.basicConfig(level=logging.WARNING)

# Start sentry
sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENV)
es = get_es()

# create db tables
models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/login")

# init FastAPI
app = FastAPI()


# basic user creation endpoint to learn SQLAlchemy
@app.post("/api/register/", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(user)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/api/login")
def login(res: Response, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
    db_user = authenticate_user(user, db)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(db_user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    res.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    del db_user.hashed_password
    return {db_user}


@app.get("/api/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# hello word example
@app.get("/api/")
def home():
    return {"hello": "world"}


# check elasticsearch connection
@app.get("/api/ping")
def ping():
    ping = es.ping()

    logging.info(f"ping: {ping}")
    return {"ping": ping}


@app.get("/api/info")
def info():
    info = es.info()
    logging.info(f"{info}")
    return {"info": info}


class Tweet(BaseModel):
    _d_: dict
    meta: dict


# demo endpoint
@app.get("/api/tweetQuery")
def tweetQuery(query: str, current_user: User = Depends(get_current_user)):

    a_like_count = A("sum", field="like_count")
    a_retweet_count = A("sum", field="retweet_count")
    a_keywords = A("significant_text", field="text")

    search = Search(using=es, index="tweets-*").query("match", text=query)

    search.aggs.bucket("total_likes", a_like_count)
    search.aggs.bucket("total_retweets", a_retweet_count)
    search.aggs.bucket("keywords", a_keywords)

    res = search.execute().to_dict()

    tweets = {}
    ids = ""
    for tweet in res["hits"]["hits"]:
        tweets[tweet["_id"]] = tweet
        ids += tweet["_id"] + ","

    ids = ids[:-1]

    updated_tweets = tweet_update(tweets, ids)

    return updated_tweets

    # return {"result": result_dict}


@app.on_event("shutdown")
def app_shutdown():
    # closes elasticsearch connection
    logging.WARNING("shutting down Elasticsearch")
    es.close()


# run uvicorn server
if __name__ == "__main__":
    uvicorn.run(app)
