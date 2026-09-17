from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models import Comment, Post, User, SubscriptionPlan
from schemas import CommentCreate, CommentResponse
from auth import get_current_user
from email_utils import send_email
from routers.posts import check_active_subscription


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
    check_active_subscription(current_user)
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == current_user.subscription_plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=400,
            detail="No active subscription plan found"
        )

    if plan.comment_limit is not None:
        comment_count = db.query(Comment).filter(
            Comment.user_id == current_user.id
        ).count()

        if comment_count >= plan.comment_limit:
            raise HTTPException(
                status_code=403,
                detail="You’ve reached your plan limit. Kindly upgrade your plan to continue."
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