from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Payment
from django.conf import settings

@shared_task
def expire_pending_payments():
    print("Running expire_pending_payments task...")

    PAYMENT_EXPIRATION_MINUTES = settings.SYSTEM_PAYMENT_EXPIRE_MINUTES

    now = timezone.now()
    expiration_time = now - timedelta(minutes=PAYMENT_EXPIRATION_MINUTES)

    # نجيب كل الـ pending payments اللي مر عليهم أكتر من 30 دقيقة
    payments = Payment.objects.filter(
        status="pending",
        created_at__lt=expiration_time
    )

    with transaction.atomic():
        updated_count = payments.update(status="canceled")

    return f"Marked {updated_count} pending payments as canceled."