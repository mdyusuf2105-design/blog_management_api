from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import engine, Base
import models

from routers import auth, posts, comments, likes, subscription
from routers import dashboard
from routers import notifications

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Blog Management API",
    description="Mini blogging system using FastAPI, SQLite and SQLAlchemy",
    version="1.0.0"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEDIA_POSTS_DIR = Path("media/posts").resolve()

app.mount(
    "/media/posts",
    StaticFiles(directory=str(MEDIA_POSTS_DIR)),
    name="media"
)

MEDIA_INVOICES_DIR = Path("media/invoices").resolve()
MEDIA_INVOICES_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/media/invoices",
    StaticFiles(directory=str(MEDIA_INVOICES_DIR)),
    name="invoices"
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(subscription.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)

@app.get("/")
def home():
    return {
        "message": "Blog Management API is running"
    }