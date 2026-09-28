from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from database import get_db
from models import Post


scheduler = BackgroundScheduler()


def publish_scheduled_posts():
    db = next(get_db())

    try:
        now = datetime.utcnow()

        scheduled_posts = (
            db.query(Post)
            .filter(
                Post.status == "scheduled",
                Post.scheduled_at.isnot(None),
                Post.scheduled_at <= now,
            )
            .all()
        )

        for post in scheduled_posts:
            post.status = "published"
            post.published_at = now
            post.scheduled_at = None

        if scheduled_posts:
            db.commit()

            print(
                f"Automatically published "
                f"{len(scheduled_posts)} scheduled post(s)."
            )

    except Exception as e:
        db.rollback()
        print(f"Scheduled publishing error: {e}")

    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            publish_scheduled_posts,
            "interval",
            seconds=30,
            id="scheduled_blog_publisher",
            replace_existing=True,
        )

        scheduler.start()

        print("Scheduled blog publisher started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Scheduled blog publisher stopped.")