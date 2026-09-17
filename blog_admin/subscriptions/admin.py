from django.contrib import admin
from .models import SubscriptionPlans, BillingHistory


@admin.register(SubscriptionPlans)
class SubscriptionPlansAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "post_limit", "images_per_post")
    search_fields = ("name",)


@admin.register(BillingHistory)
class BillingHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "plan_id",
        "price",
        "transaction_id",
        "start_date",
        "end_date",
        "invoice_path",
    )
    search_fields = ("transaction_id",)