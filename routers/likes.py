from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models import Like, Post, User
from auth import get_current_user
from email_utils import send_email


router = APIRouter(
    prefix="/posts",
    tags=["Likes"]
)


@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=400,
            detail="You already liked this post"
        )

    new_like = Like(
        post_id=post_id,
        user_id=current_user.id
    )

    db.add(new_like)
    db.commit()

    background_tasks.add_task(
        send_email,
        post.author.email,
        "Someone liked your blog post",
        f"Someone liked your post '{post.title}'."
    )

    return {
        "message": "Post liked successfully"
    }


@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(
            status_code=404,
            detail="Like not found"
        )

    db.delete(like)
    db.commit()

    return {
        "message": "Post unliked successfully"
    }