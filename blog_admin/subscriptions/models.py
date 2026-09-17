# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class SubscriptionPlans(models.Model):
    name = models.CharField()
    price = models.IntegerField()
    post_limit = models.IntegerField(blank=True, null=True)
    images_per_post = models.IntegerField(blank=True, null=True)
    like_limit = models.IntegerField(blank=True, null=True)
    comment_limit = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subscription_plans'


class BillingHistory(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING)
    plan = models.ForeignKey(SubscriptionPlans, models.DO_NOTHING)
    price = models.IntegerField()
    transaction_id = models.CharField()
    invoice_path = models.CharField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing_history'
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models



class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    subscription_plan = models.ForeignKey(
        'SubscriptionPlans',
        models.DO_NOTHING,
        blank=True,
        null=True
    )
    subscription_start = models.DateTimeField(blank=True, null=True)
    subscription_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
