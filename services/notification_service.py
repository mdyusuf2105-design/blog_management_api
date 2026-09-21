
from datetime import datetime

from services.email_service import send_email


def send_post_notification(
    recipient_email: str,
    post_title: str,
    actor_name: str,
    activity: str,
) -> bool:
    """
    Send a notification when someone likes or comments
    on a user's blog post.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    subject = f"New activity on your post: {post_title}"

    body = (
        f"Hello,\n\n"
        f"Someone has interacted with your blog post.\n\n"
        f"Post: “{post_title}”\n"
        f"User: {actor_name}\n"
        f"Activity: {activity}\n"
        f"Time: {timestamp}\n\n"
        f"Regards,\n"
        f"Blog Management Team"
    )

    return send_email(
        to_email=recipient_email,
        subject=subject,
        body=body,
    )