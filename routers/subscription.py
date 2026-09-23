
from datetime import date, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import SubscriptionPlan, BillingHistory, User
from auth import get_current_user
from invoice_utils import generate_invoice
from services.in_app_notification_service import (
    create_in_app_notification
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


def has_active_subscription(user: User) -> bool:
    if not user.subscription_end:
        return False

    end_date = user.subscription_end

    if isinstance(end_date, datetime):
        end_date = end_date.date()

    return end_date >= date.today()


@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    return db.query(SubscriptionPlan).all()


@router.post("/upgrade/{plan_id}")
def upgrade_subscription(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found"
        )

    # Check whether the user already has an active subscription.
    is_renewal = has_active_subscription(current_user)

    start_date = date.today()
    end_date = start_date + timedelta(days=30)

    current_user.subscription_plan_id = plan.id
    current_user.subscription_start = start_date
    current_user.subscription_end = end_date

    billing = BillingHistory(
        user_id=current_user.id,
        plan_id=plan.id,
        price=plan.price,
        transaction_id=f"TEST-{uuid4().hex[:12].upper()}",
        start_date=start_date,
        end_date=end_date
    )

    db.add(billing)
    db.commit()
    db.refresh(billing)

    invoice_path = generate_invoice(
        billing_id=billing.id,
        username=current_user.username,
        plan_name=plan.name,
        price=plan.price,
        start_date=start_date,
        end_date=end_date,
        transaction_id=billing.transaction_id
    )

    billing.invoice_path = invoice_path

    db.commit()
    db.refresh(current_user)
    db.refresh(billing)

    # Create an in-app notification after the subscription is updated.
    notification_message = (
        f"Your subscription to {plan.name} "
        f"{'has been renewed' if is_renewal else 'has been activated'}."
    )

    create_in_app_notification(
        db=db,
        user_id=current_user.id,
        message=notification_message,
        notification_type=(
            "subscription_renewal"
            if is_renewal
            else "subscription"
        )
    )

    return {
        "message": "Subscription updated successfully",
        "plan": plan.name,
        "start_date": start_date,
        "end_date": end_date,
        "billing_id": billing.id,
        "transaction_id": billing.transaction_id
    }


@router.get("/billing-history")
def get_billing_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(BillingHistory).filter(
        BillingHistory.user_id == current_user.id
    ).order_by(BillingHistory.id.desc()).all()

    return history


@router.get("/my-subscription")
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == current_user.subscription_plan_id
    ).first()

    return {
        "username": current_user.username,
        "plan": plan.name if plan else "No plan",
        "start_date": current_user.subscription_start,
        "end_date": current_user.subscription_end
    }