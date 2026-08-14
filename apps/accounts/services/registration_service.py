from math import remainder

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.accounts.constants import (
    REGISTRATION_DATA_PREFIX,
    OTP_REGISTER_PREFIX,
    RESEND_COOLDOWN_SECONDS,
)
from apps.accounts.exceptions import (
    EmailAlreadyExistsException,
    InvalidOTPException,
    RegistrationDataExpiredException,
    ResendOTPCooldownException,
    UsernameAlreadyExistsException,
)
from apps.accounts.models import User

from .email_service import EmailService
from .otp_service import OTPService
from .token_service import TokenService


class RegistrationService:

    @staticmethod
    def _registration_key(email: str) -> str:
        return f"{REGISTRATION_DATA_PREFIX}:{email.lower()}"

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
            raise UsernameAlreadyExistsException("Username is already taken.")

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
            raise InvalidOTPException("Invalid or expired OTP.")

        registration_data = cache.get(cls._registration_key(email))

        if registration_data is None:
            raise RegistrationDataExpiredException("Registration session has expired.")

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

        tokens = TokenService.generate_tokens(user)

        cache.delete(cls._registration_key(email))

        return {
            "user": user,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }

    @classmethod
    def resend_registration_otp(cls, email: str) -> None:
        email = email.strip().lower()
        key = cls._registration_key(email)

        registration_data = cache.get(key)
        if not registration_data:
            raise RegistrationDataExpiredException(
                "Registration session expired. Please fill out the registration form again."
            )

        cache.touch(key, timeout=settings.OTP_EXPIRATION_SECONDS)

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
    def resend_registration_otp(cls, email: str) -> None:
        email = email.strip().lower()
        key = cls._registration_key(email)

        registration_data = cache.get(key)
        if not registration_data:
            raise RegistrationDataExpiredException(
                "Registration session expired. Please fill out the registration form again."
            )

        remaining_ttl = OTPService.get_ttl(OTP_REGISTER_PREFIX,email)

        if remaining_ttl > 0:
            elapsed_seconds = settings.OTP_EXPIRATION_SECONDS - remaining_ttl

            if elapsed_seconds < RESEND_COOLDOWN_SECONDS:
                wait_time = RESEND_COOLDOWN_SECONDS - elapsed_seconds
                raise ResendOTPCooldownException(remaining_seconds=wait_time)


        cache.touch(key, timeout=settings.OTP_EXPIRATION_SECONDS)

        OTPService.delete(OTP_REGISTER_PREFIX, email)
        otp = OTPService.generate(OTP_REGISTER_PREFIX, email)

        EmailService.send_otp_email(
            recipient_email=email,
            otp=otp
        )
