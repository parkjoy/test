# coding=utf-8
from django.db.models.signals import post_save
from django.dispatch import receiver
from mx_user.models import UserProfile
# @receiver(post_save, sender=UserProfile)
# def create_user(sender, instance=None, created=False, **kwargs):
#     if created:
#         instance.set_password(instance.password)
#         instance.save()