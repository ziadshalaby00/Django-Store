from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from .models import Address
from .serializers import AddressSerializer

class UserAddressAPIView(APIView):
    """
    CRUD كامل على عنوان المستخدم بدون الحاجة لإرسال أي ID
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return user.address
        except Address.DoesNotExist:
            return None

    def get(self, request):
        # GET /address/ -> عرض العنوان
        obj = self.get_object()
        if not obj:
            return Response({"detail": "Address not set."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AddressSerializer(obj)
        return Response(serializer.data)

    def post(self, request):
        # POST /address/ -> إنشاء عنوان جديد
        user = request.user
        if hasattr(user, "address"):
            raise serializers.ValidationError("Address already exists.")
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def patch(self, request):
        # PATCH /address/ -> تعديل بعض الحقول فقط
        obj = self.get_object()
        if not obj:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AddressSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        # DELETE /address/ -> حذف العنوان
        obj = self.get_object()
        if not obj:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"detail": "Address deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
