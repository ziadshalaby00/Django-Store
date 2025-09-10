from django.shortcuts import render

# Create your views here.
from .models import Address
from .serializers import AddressSerializer
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # يرجع بس عناوين اليوزر الحالي
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({"label": "You already have an address with this label."})
