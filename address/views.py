from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from .models import Address
from .serializers import AddressSerializer
from django.db.models import ProtectedError

class UserAddressAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
            # لو مفيش ID -> جلب كل العناوين
            addresses = Address.objects.filter(user=request.user)
            serializer = AddressSerializer(addresses, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if address.shipping_orders.exists():  # shipping_orders هي related_name في موديل Order
            return Response(
                {"detail": "Cannot edit this address because it is linked to existing orders."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AddressSerializer(address, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            address.delete()
            return Response({"detail": "Address deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete this address because it is linked to existing orders."},
                status=status.HTTP_400_BAD_REQUEST
            )