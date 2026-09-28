from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models

from routers import (
    auth,
    posts,
    comments,
    likes,
    subscription,
    dashboard,
    notifications,
    ai_support,
    auth0,
)

from scheduler import start_scheduler, stop_scheduler


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Blog Management API",
    description="Mini blogging system using FastAPI, SQLite and SQLAlchemy",
    version="1.0.0",
)


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
    name="media",
)


MEDIA_INVOICES_DIR = Path("media/invoices").resolve()
MEDIA_INVOICES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

app.mount(
    "/media/invoices",
    StaticFiles(directory=str(MEDIA_INVOICES_DIR)),
    name="invoices",
)


# Routers
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(subscription.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)
app.include_router(ai_support.router)
app.include_router(auth0.router)


# Start automatic scheduled blog publishing
@app.on_event("startup")
def startup_event():
    start_scheduler()


# Stop scheduler when application shuts down
@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


@app.get("/")
def home():
    return {
        "message": "Blog Management API is running"
    }