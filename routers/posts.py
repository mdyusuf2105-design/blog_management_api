import os
import shutil
import uuid
import math
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    Form,
    UploadFile,
    Query,
)
from sqlalchemy.orm import Session

from database import get_db
from models import Post, User
from schemas import PostResponse, PaginatedPostResponse
from auth import get_current_user


router = APIRouter(prefix="/posts", tags=["Posts"])


MEDIA_POSTS_DIR = Path("media/posts")
MEDIA_POSTS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/jpg",
    "image/webp",
}


def save_image(image: UploadFile) -> str:
    extension = Path(image.filename or "").suffix.lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, GIF and WEBP images are allowed"
        )

    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = MEDIA_POSTS_DIR / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/media/posts/{filename}"


@router.post("/", response_model=PostResponse)
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url = None

    if image:
        image_url = save_image(image)

    new_post = Post(
        title=title,
        content=content,
        author_id=current_user.id,
        image=image_url,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=PaginatedPostResponse)
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Post)

    # Search by title or content
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Post.title.ilike(search_term)) |
            (Post.content.ilike(search_term))
        )

    # Total matching posts
    total_count = query.count()

    # Calculate total pages
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 0

    # Pagination
    posts = (
        query
        .order_by(Post.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "posts": posts,
        "total_count": total_count,
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
    }


@router.get("/mine", response_model=list[PostResponse])
def get_my_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Post).filter(
        Post.author_id == current_user.id
    ).all()


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own posts"
        )

    post.title = title
    post.content = content

    if image:
        # Delete old image if one exists
        if post.image:
            old_image_path = Path(post.image.lstrip("/"))

            if old_image_path.is_file():
                os.remove(old_image_path)

        # Save new image
        post.image = save_image(image)

    db.commit()
    db.refresh(post)

    return post


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own posts"
        )

    # Delete image from disk
    if post.image:
        image_path = Path(post.image.lstrip("/"))

        if image_path.is_file():
            os.remove(image_path)

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully"
    }