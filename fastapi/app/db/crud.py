from app.db.database import get_db
from sqlalchemy.orm import Session
from . import models, schemas
from .hashing import ph
from fastapi import Depends


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    hashed_password = ph.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(user: schemas.UserAuthenticate, db: Session):
    db_user = get_user_by_email(db, user.email)

    # print("db_user: ", db_user)

    if not db_user:
        return False

    if not ph.verify(db_user.hashed_password, user.password):
        return False

    return db_user
