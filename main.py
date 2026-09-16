from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import engine, Base
import models

from routers import auth, posts, comments, likes


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Blog Management API",
    description="Mini blogging system using FastAPI, SQLite and SQLAlchemy",
    version="1.0.0"
)


MEDIA_POSTS_DIR = Path("media/posts").resolve()

app.mount(
    "/media/posts",
    StaticFiles(directory=str(MEDIA_POSTS_DIR)),
    name="media"
)



app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)


@app.get("/")
def home():
    return {
        "message": "Blog Management API is running"
    }