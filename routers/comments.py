from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models import Comment, Post, User
from schemas import CommentCreate, CommentResponse
from auth import get_current_user
from email_utils import send_email


router = APIRouter(
    prefix="/posts",
    tags=["Comments"]
)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse
)
def add_comment(
    post_id: int,
    comment: CommentCreate,
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

    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        text=comment.text
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    background_tasks.add_task(
        send_email,
        post.author.email,
        "New comment on your blog post",
        f"Someone commented on your post '{post.title}'.\n\n"
        f"Comment: {comment.text}"
    )

    return new_comment


@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse]
)
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return db.query(Comment).filter(
        Comment.post_id == post_id
    ).all()