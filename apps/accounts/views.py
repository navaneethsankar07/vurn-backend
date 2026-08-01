from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from apps.accounts.serializers import SendOTPSerializer, RegisterSerializer
from apps.accounts.services.registration_service import RegistrationService
from apps.accounts.exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    InvalidOTPException,
    RegistrationDataExpiredException,
)


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
