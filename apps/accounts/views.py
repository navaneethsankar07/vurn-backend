from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .exceptions import (
    EmailAlreadyExistsException,
    EmailNotVerifiedException,
    InactiveAccountException,
    InvalidCredentialsException,
    UsernameAlreadyExistsException,
    InvalidOTPException,
    RegistrationDataExpiredException,
)
from .serializers import (
    CurrentUserSerializer,
    LoginSerializer,
    SendOTPSerializer,
    RegisterSerializer,
)
from .services.login_service import LoginService
from .services.logout_service import LogoutService
from .services.profile_service import ProfileService
from .services.registration_service import RegistrationService


class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            RegistrationService.send_registration_otp(serializer.validated_data)

            return Response(
                {"message": "OTP sent successfully."},
                status=status.HTTP_200_OK,
            )

        except EmailAlreadyExistsException as exc:
            return Response(
                {"email": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except UsernameAlreadyExistsException as exc:
            return Response(
                {"username": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = RegistrationService.register(**serializer.validated_data)

            user = result["user"]

            response = Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                    "access": result["access"],
                },
                status=status.HTTP_201_CREATED,
            )

            response.set_cookie(
                key="refresh_token",
                value=result["refresh"],
                max_age=int(
                    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
                ),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/api/v1/auth/",
            )

            return response

        except InvalidOTPException as exc:
            return Response(
                {"otp": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except RegistrationDataExpiredException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            result = LoginService.login(**serializer.validated_data)

            user = result["user"]

            response = Response(
                {
                    "message": "Login successful.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                    "access": result["access"],
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="refresh_token",
                value=result["refresh"],
                max_age=int(
                    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
                ),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/api/v1/auth/",
            )

            return response

        except InvalidCredentialsException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except EmailNotVerifiedException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        except InactiveAccountException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )


class RefreshTokenView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"error": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(
            data={
                "refresh": refresh_token,
            }
        )

        serializer.is_valid(raise_exception=True)

        response = Response(
            {
                "access": serializer.validated_data["access"],
            },
            status=status.HTTP_200_OK,
        )

        if "refresh" in serializer.validated_data:
            response.set_cookie(
                key="refresh_token",
                value=serializer.validated_data["refresh"],
                max_age=int(
                    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
                ),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/api/v1/auth/",
            )

        return response


class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"error": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            LogoutService.logout(refresh_token)

            response = Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK,
            )

            response.delete_cookie(
                key="refresh_token",
                path="/api/v1/auth/",
                samesite="Lax",
            )

            return response

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = ProfileService.get_current_user(request.user)

        serializer = CurrentUserSerializer(user)

        return Response(serializer.data)
