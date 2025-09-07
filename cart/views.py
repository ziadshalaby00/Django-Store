

# Create your views here.
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from product.models import Product


class CartView(generics.RetrieveAPIView):
    """Get current user's cart"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(generics.CreateAPIView):
    """Add a product to cart"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )
        if not created:
            return Response(
                {
                    "detail": "Product already in cart"
                },
                status=status.HTTP_200_OK,
            )

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateCartItemView(generics.UpdateAPIView):
    """Update quantity of a cart item"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def patch(self, request, *args, **kwargs):
        cart_item = self.get_object()
        if cart_item.cart.user != request.user:
            return Response({"detail": "Not allowed"}, status=403)

        quantity = int(request.data.get("quantity", 1))
        if quantity < 1:
            cart_item.delete()
            return Response({"detail": "Item removed"}, status=204)

        cart_item.quantity = quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)


class RemoveFromCartView(generics.DestroyAPIView):
    """Remove item from cart"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def delete(self, request, *args, **kwargs):
        cart_item = self.get_object()
        if cart_item.cart.user != request.user:
            return Response({"detail": "Not allowed"}, status=403)

        cart_item.delete()
        return Response({"detail": "Item removed"}, status=204)


class ClearCartView(generics.DestroyAPIView):
    """Clear all items from cart"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared"}, status=204)
