
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Post, Comment, Like
from auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["User Dashboard"]
)


@router.get("/dashboard/")
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Total posts created by the logged-in user
    total_posts = (
        db.query(func.count(Post.id))
        .filter(Post.author_id == current_user.id)
        .scalar()
    )

    # 2. Total comments made by the logged-in user
    total_comments = (
        db.query(func.count(Comment.id))
        .filter(Comment.user_id == current_user.id)
        .scalar()
    )

    # 3. Total likes received on the user's own posts
    total_likes_received = (
        db.query(func.count(Like.id))
        .join(Post, Like.post_id == Post.id)
        .filter(Post.author_id == current_user.id)
        .scalar()
    )

    # 4. Views are not tracked in the current models
    total_views = 0

    # 5. Per-post comment counts
    comment_counts = (
        db.query(
            Comment.post_id.label("post_id"),
            func.count(Comment.id).label("comments_count")
        )
        .group_by(Comment.post_id)
        .subquery()
    )

    # 6. Per-post like counts
    like_counts = (
        db.query(
            Like.post_id.label("post_id"),
            func.count(Like.id).label("likes_count")
        )
        .group_by(Like.post_id)
        .subquery()
    )

    # 7. Get this user's posts with their individual counts
    post_analytics = (
        db.query(
            Post.id,
            Post.title,
            func.coalesce(
                comment_counts.c.comments_count, 0
            ).label("comments_count"),
            func.coalesce(
                like_counts.c.likes_count, 0
            ).label("likes_count")
        )
        .outerjoin(
            comment_counts,
            comment_counts.c.post_id == Post.id
        )
        .outerjoin(
            like_counts,
            like_counts.c.post_id == Post.id
        )
        .filter(Post.author_id == current_user.id)
        .order_by(Post.id)
        .all()
    )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_posts": total_posts or 0,
        "total_comments": total_comments or 0,
        "total_likes_received": total_likes_received or 0,
        "total_views": total_views,
        "post_analytics": [
            {
                "post_id": post.id,
                "title": post.title,
                "comments_count": post.comments_count,
                "likes_count": post.likes_count
            }
            for post in post_analytics
        ]
    }