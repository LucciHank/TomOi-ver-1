from celery import shared_task
from django.utils import timezone
from accounts.models import CustomUser

@shared_task
def delete_expired_accounts():
    expired_users = CustomUser.objects.filter(
        is_active=False,
        verification_token_expires__lt=timezone.now()
    )
    expired_users.delete() 