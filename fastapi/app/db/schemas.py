from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str


class UserAuthenticate(UserBase):
    password: str


class UserCreate(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
