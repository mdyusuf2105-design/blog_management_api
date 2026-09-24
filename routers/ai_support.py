from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import get_current_user


router = APIRouter(
    prefix="/api/ai-support",
    tags=["AI Support"]
)


def generate_ai_response(message: str) -> str:
    """
    Generate a predefined AI support response
    based on common Blog Management questions.
    """

    message = message.lower().strip()

    # Create posts
    if (
        "create post" in message
        or "create a post" in message
        or "new post" in message
        or "how to post" in message
    ):
        return (
            "To create a post, open the Posts section and choose "
            "the option to create a new post. Enter your title and "
            "content, then submit the post."
        )

    # Edit posts
    if (
        "edit post" in message
        or "edit a post" in message
        or "update post" in message
    ):
        return (
            "To edit a post, open your Posts section, select the "
            "post you want to modify, choose Edit, update the "
            "content, and save your changes."
        )

    # Delete posts
    if (
        "delete post" in message
        or "delete a post" in message
        or "remove post" in message
    ):
        return (
            "To delete a post, open your Posts section, select "
            "your post, and use the Delete option. Please make "
            "sure you want to remove the post before confirming."
        )

    # Subscription
    if (
        "subscription" in message
        or "plan" in message
        or "upgrade" in message
        or "renew" in message
    ):
        return (
            "You can manage your subscription from the "
            "Subscriptions section. You can view available plans, "
            "upgrade your plan, and renew your subscription."
        )

    # Billing
    if (
        "billing" in message
        or "payment" in message
        or "invoice" in message
        or "transaction" in message
    ):
        return (
            "Your billing information and previous transactions "
            "can be viewed from the Billing History section. "
            "Invoices are generated after successful subscription "
            "transactions."
        )

    # Profile
    if (
        "profile" in message
        or "account" in message
        or "username" in message
    ):
        return (
            "You can manage your account information from your "
            "profile or account section. Your account information "
            "is associated with your authenticated user account."
        )

    # Dashboard
    if (
        "dashboard" in message
        or "analytics" in message
        or "statistics" in message
        or "stats" in message
    ):
        return (
            "The User Dashboard shows your blog activity, including "
            "total posts, comments, likes received, and views. "
            "It also provides charts for analyzing your post "
            "engagement."
        )

    # Notifications
    if (
        "notification" in message
        or "notifications" in message
    ):
        return (
            "The notification center shows important activity such "
            "as likes, comments, and subscription updates. You can "
            "mark individual notifications or all notifications "
            "as read."
        )

    # Help
    if (
        "help" in message
        or "what can you do" in message
        or "what can i ask" in message
    ):
        return (
            "I can help you with creating, editing, and deleting "
            "posts, subscriptions, billing, profile management, "
            "dashboard analytics, notifications, and general "
            "Blog Management questions."
        )

    # Greeting
    if (
        "hello" in message
        or "hi" in message
        or "hey" in message
    ):
        return (
            "Hello! 👋 I'm your Blog Management Support Assistant. "
            "How can I help you today?"
        )

    # Default response
    return (
        "I'm here to help with the Blog Management platform. "
        "You can ask me about creating posts, editing or deleting "
        "posts, subscriptions, billing, your profile, dashboard "
        "analytics, or notifications."
    )


@router.post("/")
def ai_support(
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    response = generate_ai_response(message)

    return {
        "user_id": current_user.id,
        "message": message,
        "response": response,
    }