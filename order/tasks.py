from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Order
from django.conf import settings

@shared_task
def clean_unpaid_orders():
    print("Running clean_unpaid_orders task...")
    
    now = timezone.now()

    cod_orders = Order.objects.filter(
        payment_method="cod",
        is_paid=False,
        created_at__lt=now - timedelta(days=settings.COD_ORDER_EXPIRE_DAYS)
    ).exclude(
        payment_status="expired"
    ).distinct()

    epay_orders = Order.objects.filter(
        payment_method="EPAY",
        is_paid=False,
        created_at__lt=now - timedelta(minutes=settings.ORDER_EXPIRE_MINUTES)
    ).exclude(
        payments__status="pending"   # استبعد اللي عنده pending
    ).exclude(
        payment_status="expired"
    ).distinct()

    with transaction.atomic():
        for order in cod_orders:
            order.set_status("expired") # signal OrderItem يرجع المخزون تلقائيًا

        for order in epay_orders:
            order.set_status("expired") # signal OrderItem يرجع المخزون تلقائيًا

    return f"Expired {cod_orders.count()} unpaid COD orders and {epay_orders.count()} unpaid EPAY orders."
