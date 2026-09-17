
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models import Like, Post, User, SubscriptionPlan
from auth import get_current_user
from email_utils import send_email
from routers.posts import check_active_subscription


router = APIRouter(
    prefix="/posts",
    tags=["Likes"]
)

PLAN_LIMIT_MESSAGE = (
    "You’ve reached your plan limit. Kindly upgrade your plan to continue."
)


@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check whether the post exists
    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # Check whether the user's subscription is active
    check_active_subscription(current_user)

    # Check whether the user already liked this post
    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id,
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=400,
            detail="You already liked this post",
        )

    # Get the user's subscription plan
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == current_user.subscription_plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=400,
            detail="No active subscription plan found",
        )

    # Check the like limit
    if plan.like_limit is not None:
        like_count = db.query(Like).filter(
            Like.user_id == current_user.id
        ).count()

        if like_count >= plan.like_limit:
            raise HTTPException(
                status_code=403,
                detail=PLAN_LIMIT_MESSAGE,
            )

    # Create the like
    new_like = Like(
        post_id=post_id,
        user_id=current_user.id,
    )

    db.add(new_like)
    db.commit()

    # Send notification email
    background_tasks.add_task(
        send_email,
        post.author.email,
        "Someone liked your blog post",
        f"Someone liked your post '{post.title}'.",
    )

    return {
        "message": "Post liked successfully"
    }


@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id,
    ).first()

    if not like:
        raise HTTPException(
            status_code=404,
            detail="Like not found",
        )

    db.delete(like)
    db.commit()

    return {
        "message": "Post unliked successfully"
    }