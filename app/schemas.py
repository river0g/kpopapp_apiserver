from pydantic import BaseModel
from typing import Optional


class UserBody(BaseModel):
    username: str
    password: str


class SuperUserBody(BaseModel):
    username: str
    password: str
    master: str


class Articles(BaseModel):
    _id: Optional[str] = None
    title: str
    detail: str
    url: str
    thumbnail: str
    date: str
    datetime: int
    author: str
    group: list
    group_id: list
    source_site: str
    source_site_id: str


class Status(BaseModel):
    status: str
    message: str


class JwtToken(BaseModel):
    token: str
