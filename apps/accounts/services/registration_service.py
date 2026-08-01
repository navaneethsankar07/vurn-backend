from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.constants import (
    REGISTRATION_DATA_PREFIX,
    OTP_REGISTER_PREFIX,
)
from apps.accounts.exceptions import (
    EmailAlreadyExistsException,
    InvalidOTPException,
    RegistrationDataExpiredException,
    UsernameAlreadyExistsException,
)
from apps.accounts.models import User
from apps.accounts.services.email_service import EmailService
from apps.accounts.services.otp_service import OTPService


class RegistrationService:

    @staticmethod
    def _registration_key(email: str) -> str:
        return f"{REGISTRATION_DATA_PREFIX}:{email.lower()}"

    @staticmethod
    def _generate_tokens(user: User) -> dict:
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @classmethod
    def send_registration_otp(cls, validated_data: dict) -> None:
        email = validated_data["email"].lower()
        username = validated_data["username"].lower()

        if User.objects.filter(
            email=email,
            is_email_verified=True,
        ).exists():
            raise EmailAlreadyExistsException(
                "An account with this email already exists."
            )

        if User.objects.filter(username=username).exists():
            raise UsernameAlreadyExistsException(
                "Username is already taken."
            )

        registration_data = {
            "email": email,
            "username": username,
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "password": make_password(validated_data["password"]),
        }

        cache.set(
            cls._registration_key(email),
            registration_data,
            timeout=settings.OTP_EXPIRATION_SECONDS,
        )

        OTPService.delete(
            OTP_REGISTER_PREFIX,
            email,
        )

        otp = OTPService.generate(
            OTP_REGISTER_PREFIX,
            email,
        )

        EmailService.send_otp_email(
            recipient_email=email,
            otp=otp,
        )

    @classmethod
    @transaction.atomic
    def register(
        cls,
        email: str,
        otp: str,
    ) -> dict:
        email = email.strip().lower()

        if not OTPService.verify(
            OTP_REGISTER_PREFIX,
            email,
            otp,
        ):
            raise InvalidOTPException(
                "Invalid or expired OTP."
            )

        registration_data = cache.get(
            cls._registration_key(email)
        )

        if registration_data is None:
            raise RegistrationDataExpiredException(
                "Registration session has expired."
            )

        user = User.objects.create_user(
            email=registration_data["email"],
            username=registration_data["username"],
            first_name=registration_data["first_name"],
            last_name=registration_data["last_name"],
            password=registration_data["password"],
            password_is_hashed=True,
            is_active=True,
            is_email_verified=True,
        )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        tokens = cls._generate_tokens(user)

        cache.delete(
            cls._registration_key(email)
        )

        return {
            "user": user,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }