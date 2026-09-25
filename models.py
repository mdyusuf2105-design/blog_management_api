from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey,
    DateTime, Date, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    subscription_plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=True
    )

    subscription_start = Column(DateTime(timezone=True), nullable=True)
    subscription_end = Column(DateTime(timezone=True), nullable=True)

    subscription_plan = relationship(
    "SubscriptionPlan",
    back_populates="users"
)

    billing_history = relationship(
        "BillingHistory",
        back_populates="user"
    )

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")
    images = relationship(
        "PostImage",
        back_populates="post",
        cascade="all, delete-orphan"
    )

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)

    post_limit = Column(Integer, nullable=True)
    images_per_post = Column(Integer, nullable=True)
    like_limit = Column(Integer, nullable=True)
    comment_limit = Column(Integer, nullable=True)

    users = relationship(
        "User",
        back_populates="subscription_plan"
    )


class BillingHistory(Base):
    __tablename__ = "billing_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=False
    )

    price = Column(Integer, nullable=False)
    transaction_id = Column(String, unique=True, nullable=False)
    invoice_path = Column(String, nullable=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="billing_history"
    )

    plan = relationship("SubscriptionPlan")

class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(
        Integer,
        ForeignKey("posts.id"),
        nullable=False
    )
    image_path = Column(String, nullable=False)

    post = relationship(
        "Post",
        back_populates="images"
    )


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    message = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="notifications"
    )

class AISupportActivity(Base):
    __tablename__ = "ai_support_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(String, nullable=False)
    ai_response = Column(String, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User")