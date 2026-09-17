from database import SessionLocal
from models import SubscriptionPlan

db = SessionLocal()

plans = [
    {
        "name": "Basic",
        "price": 0,
        "post_limit": 1,
        "images_per_post": 1,
        "like_limit": 10,
        "comment_limit": 5,
    },
    {
        "name": "Premium",
        "price": 499,
        "post_limit": 2,
        "images_per_post": 2,
        "like_limit": 100,
        "comment_limit": 50,
    },
    {
        "name": "Pro",
        "price": 999,
        "post_limit": None,
        "images_per_post": None,
        "like_limit": None,
        "comment_limit": None,
    },
]

for plan_data in plans:
    existing = db.query(SubscriptionPlan).filter_by(
        name=plan_data["name"]
    ).first()

    if not existing:
        db.add(SubscriptionPlan(**plan_data))

db.commit()
db.close()

print("Subscription plans added successfully.")