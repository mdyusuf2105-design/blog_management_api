import os
import shutil
import uuid
import math
from pathlib import Path
from datetime import date, datetime, timezone

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
from models import Post, User, SubscriptionPlan, PostImage
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

PLAN_LIMIT_MESSAGE = (
    "You’ve reached your plan limit. Kindly upgrade your plan to continue."
)


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
            detail="Only JPG, JPEG, PNG, GIF and WEBP images are allowed",
        )

    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = MEDIA_POSTS_DIR / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/media/posts/{filename}"


def check_active_subscription(user: User):
    end_date = user.subscription_end

    if not end_date:
        raise HTTPException(
            status_code=403,
            detail="Your subscription has expired. Please renew your plan.",
        )

    if isinstance(end_date, datetime):
        end_date = end_date.date()

    if end_date < date.today():
        raise HTTPException(
            status_code=403,
            detail="Your subscription has expired. Please renew your plan.",
        )


def normalize_scheduled_datetime(value: datetime | None):
    if value is None:
        return None

    # If the client sends a timezone-aware datetime, convert it to UTC.
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    return value


def validate_publishing_options(
    publishing_option: str,
    scheduled_at: datetime | None,
):
    allowed_options = {
        "publish_now",
        "draft",
        "schedule",
    }

    if publishing_option not in allowed_options:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid publishing option. Use "
                "'publish_now', 'draft', or 'schedule'."
            ),
        )

    if publishing_option == "draft":
        if scheduled_at is not None:
            raise HTTPException(
                status_code=400,
                detail="Draft posts cannot have scheduled_at set.",
            )

    if publishing_option == "schedule":
        if scheduled_at is None:
            raise HTTPException(
                status_code=400,
                detail="scheduled_at is required when scheduling a post.",
            )

        scheduled_at = normalize_scheduled_datetime(scheduled_at)

        now = datetime.utcnow()

        if scheduled_at <= now:
            raise HTTPException(
                status_code=400,
                detail="scheduled_at must be a future datetime.",
            )

        return scheduled_at

    if publishing_option == "publish_now":
        if scheduled_at is not None:
            raise HTTPException(
                status_code=400,
                detail="Publish Now cannot have scheduled_at set.",
            )

    return None


@router.post("/", response_model=PostResponse)
def create_post(
    title: str = Form(...),
    content: str = Form(...),

    # Publishing options:
    # publish_now / draft / schedule
    publishing_option: str = Form("publish_now"),

    # Required only when publishing_option = schedule
    scheduled_at: datetime | None = Form(None),

    image1: UploadFile | None = File(None),
    image2: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == current_user.subscription_plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=400,
            detail="No active subscription plan found",
        )

    check_active_subscription(current_user)

    # Check post limit
    if plan.post_limit is not None:
        post_count = db.query(Post).filter(
            Post.author_id == current_user.id
        ).count()

        if post_count >= plan.post_limit:
            raise HTTPException(
                status_code=403,
                detail=PLAN_LIMIT_MESSAGE,
            )

    # Check image limit
    uploaded_images = [
        image
        for image in (image1, image2)
        if image is not None and image.filename
    ]

    if (
        plan.images_per_post is not None
        and len(uploaded_images) > plan.images_per_post
    ):
        raise HTTPException(
            status_code=403,
            detail=PLAN_LIMIT_MESSAGE,
        )

    # Validate publishing option
    normalized_scheduled_at = validate_publishing_options(
        publishing_option,
        scheduled_at,
    )

    # Determine initial status
    if publishing_option == "draft":
        status = "draft"
        scheduled_value = None
        published_value = None

    elif publishing_option == "schedule":
        status = "scheduled"
        scheduled_value = normalized_scheduled_at
        published_value = None

    else:
        status = "published"
        scheduled_value = None
        published_value = datetime.utcnow()

    new_post = Post(
        title=title,
        content=content,
        author_id=current_user.id,
        image=None,
        status=status,
        scheduled_at=scheduled_value,
        published_at=published_value,
    )

    db.add(new_post)
    db.flush()

    saved_paths = []

    try:
        for index, image in enumerate(uploaded_images):
            image_url = save_image(image)
            saved_paths.append(image_url)

            if index == 0:
                new_post.image = image_url

            db.add(
                PostImage(
                    post_id=new_post.id,
                    image_path=image_url,
                )
            )

        db.commit()
        db.refresh(new_post)

    except Exception:
        db.rollback()

        for image_url in saved_paths:
            file_path = Path(image_url.lstrip("/"))

            if file_path.is_file():
                os.remove(file_path)

        raise

    return new_post


@router.get("/", response_model=PaginatedPostResponse)
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Post)

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            (Post.title.ilike(search_term))
            | (Post.content.ilike(search_term))
        )

    total_count = query.count()

    total_pages = (
        math.ceil(total_count / limit)
        if total_count > 0
        else 0
    )

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
    return (
        db.query(Post)
        .filter(Post.author_id == current_user.id)
        .all()
    )


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

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

    publishing_option: str = Form("publish_now"),
    scheduled_at: datetime | None = Form(None),

    image: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own posts",
        )

    normalized_scheduled_at = validate_publishing_options(
        publishing_option,
        scheduled_at,
    )

    post.title = title
    post.content = content

    if publishing_option == "draft":
        post.status = "draft"
        post.scheduled_at = None
        post.published_at = None

    elif publishing_option == "schedule":
        post.status = "scheduled"
        post.scheduled_at = normalized_scheduled_at
        post.published_at = None

    else:
        post.status = "published"
        post.scheduled_at = None

        if post.published_at is None:
            post.published_at = datetime.utcnow()

    if image and image.filename:
        if post.image:
            old_image_path = Path(post.image.lstrip("/"))

            if old_image_path.is_file():
                os.remove(old_image_path)

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
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own posts",
        )

    if post.image:
        image_path = Path(post.image.lstrip("/"))

        if image_path.is_file():
            os.remove(image_path)

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully"
    }