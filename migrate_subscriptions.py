from sqlalchemy import inspect, text
from database import engine, Base
import models

# Create any new tables first
Base.metadata.create_all(bind=engine)

# Add missing subscription columns to the existing users table
inspector = inspect(engine)
existing_columns = {
    column["name"]
    for column in inspector.get_columns("users")
}

new_columns = {
    "subscription_plan_id": (
        "INTEGER REFERENCES subscription_plans(id)"
    ),
    "subscription_start": "DATETIME",
    "subscription_end": "DATETIME",
}

with engine.begin() as connection:
    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            connection.execute(
                text(
                    f"ALTER TABLE users "
                    f"ADD COLUMN {column_name} {column_type}"
                )
            )
            print(f"Added column: {column_name}")
        else:
            print(f"Already exists: {column_name}")

print("Subscription database migration completed.")