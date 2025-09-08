from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Order

@shared_task
def clean_unpaid_orders():
    print("Running clean_unpaid_orders task...")
    
    now = timezone.now()

    # إعداد الفترات الزمنية
    COD_EXPIRATION_DAYS = 4
    CARD_EXPIRATION_MINUTES = 30

    cod_orders = Order.objects.filter(
        payment_method="cod",
        is_paid=False,
        created_at__lt=now - timedelta(days=COD_EXPIRATION_DAYS)
    ).exclude(
        payments__status="pending"   # استبعد اللي عنده pending
    ).exclude(
        payment_status="expired"
    ).distinct()

    card_orders = Order.objects.filter(
        payment_method="card",
        is_paid=False,
        created_at__lt=now - timedelta(minutes=CARD_EXPIRATION_MINUTES)
    ).exclude(
        payments__status="pending"   # استبعد اللي عنده pending
    ).exclude(
        payment_status="expired"
    ).distinct()

    with transaction.atomic():
        for order in cod_orders:
            order.set_status("expired") # signal OrderItem يرجع المخزون تلقائيًا

        for order in card_orders:
            order.set_status("expired") # signal OrderItem يرجع المخزون تلقائيًا

    return f"Expired {cod_orders.count()} unpaid COD orders and {card_orders.count()} unpaid Card orders."
