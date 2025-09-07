from django.urls import path
from .views import UserAddressAPIView

urlpatterns = [
    # GET كل العناوين أو POST لإنشاء عنوان جديد
    path('addresses/', UserAddressAPIView.as_view(), name='user-address-list-create'),

    # GET/ PATCH / DELETE على عنوان محدد بالـ ID
    path('addresses/<int:address_id>/', UserAddressAPIView.as_view(), name='user-address-detail'),
]
