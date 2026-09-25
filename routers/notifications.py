
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Notification, User
from auth0 import get_auth0_user

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_auth0_user)
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.timestamp.desc())
        .all()
    )

    return [
        {
            "id": notification.id,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "is_read": notification.is_read,
            "timestamp": notification.timestamp
        }
        for notification in notifications
    ]


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_auth0_user)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True
    db.commit()

    return {
        "message": "Notification marked as read",
        "notification_id": notification.id
    }


@router.patch("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_auth0_user)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update(
        {Notification.is_read: True},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "All notifications marked as read"
    }