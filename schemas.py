from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    image: str | None = None

    class Config:
        from_attributes = True

class PaginatedPostResponse(BaseModel):
    posts: list[PostResponse]
    total_count: int
    total_pages: int
    page: int
    limit: int
    
class PostUpdate(BaseModel):
    title: str
    content: str

class CommentCreate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

