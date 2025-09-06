from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "User registered successfully", "user": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  # استدعاء الكلاس الأصلي
        data = response.data

        access = data.get("access")
        refresh = data.get("refresh")

        # نرجع response جديد (من غير التوكينات في body)
        res = Response({"message": "Login successful"})

        # نحط التوكينات في cookies
        if access:
            res.set_cookie(
                key="access",
                value=access,
                httponly=True,
                secure=True,      # في production لازم يكون عندك HTTPS
                samesite="Strict" # ممكن تخليها "Lax" حسب احتياجك
            )
        if refresh:
            res.set_cookie(
                key="refresh",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="Strict"
            )

        return res
    
    
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # ناخد refresh من الكوكي
        refresh_token = request.COOKIES.get("refresh")

        if refresh_token is None:
            return Response({"error": "No refresh token in cookie"}, status=400)

        serializer = self.get_serializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        access = serializer.validated_data["access"]

        res = Response({"message": "Access token refreshed"})

        # نخزن access الجديد في الكوكي
        res.set_cookie(
            key="access",
            value=access,
            httponly=True,
            secure=True,
            samesite="Strict"
        )

        return res

from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

class CookieTokenVerifyView(TokenVerifyView):
    serializer_class = TokenVerifySerializer

    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get("access")

        if access_token is None:
            return Response(
                {"status": "no_token", "message": "No access token in cookie"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"token": access_token})

        try:
            serializer.is_valid(raise_exception=True)
            return Response(
                {"message": "Access token is valid"},
                status=status.HTTP_200_OK,
            )
        except TokenError as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except InvalidToken as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
            
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken
from google.auth.transport import requests as google_requests
from django.conf import settings

class GoogleLoginView(APIView):
    def post(self, request):
        google_token = request.data.get("token")

        if not google_token:
            return Response({"error": "No Google token provided"}, status=400)

        try:
            # تحقق من التوكين مع Google
            idinfo = id_token.verify_oauth2_token(
                google_token, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            )
            email = idinfo.get("email")
            fullname = idinfo.get("name")
            username = email.split("@")[0]

            # إنشاء أو جلب المستخدم
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": username, "fullname": fullname},
            )

            # إصدار JWT
            refresh = RefreshToken.for_user(user)
            response = Response(
                {"message": "Login successful with Google"},
                status=status.HTTP_200_OK,
            )
            
            response.set_cookie(
                key="access",
                value=str(refresh.access_token),
                httponly=True,
                secure=True,
                samesite="Strict"
            )
            response.set_cookie(
                key="refresh",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="Strict"
            )

            return response
        
        except Exception:
            return Response({"error": "Invalid Google token"}, status=400)


from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


from django.core.mail import send_mail

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=None,
            recipient_list=[email],
        )

        return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)


from rest_framework.permissions import IsAuthenticated
from .serializers import UserUpdateSerializer

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        
        # حذف الكوكيز
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        
        return response
    
    

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        password = request.data.get("password")

        if not password:
            return Response({"error": "Password is required to delete account"}, status=status.HTTP_400_BAD_REQUEST)

        # تحقق من الباسوورد
        if not user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

        # حذف المستخدم
        user.delete()

        # حذف الكوكيز
        response = Response({"message": "User account deleted successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie("access")
        response.delete_cookie("refresh")

        return response