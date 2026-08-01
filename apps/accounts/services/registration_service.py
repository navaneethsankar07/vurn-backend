import json

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.cache import cache

from apps.accounts.constants import REGISTRATION_DATA_PREFIX, OTP_REGISTER_PREFIX
from apps.accounts.models import User
from apps.accounts.services.email_service import EmailService
from apps.accounts.services.otp_service import OTPService
from apps.accounts.exceptions import EmailAlreadyExistsException, UsernameAlreadyExistsException


class RegistrationService:

    @staticmethod
    def _registration_key(email: str) -> str:
        return f"{REGISTRATION_DATA_PREFIX}:{email.lower()}"

    @classmethod
    def send_registration_otp(cls, validated_data: dict):

        email = validated_data["email"].lower()
        username = validated_data["username"].lower()

        if User.objects.filter(email=email, is_email_verified=True).exists():
            raise EmailAlreadyExistsException("An account with this email already exists.")
        
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
            json.dumps(registration_data),
            timeout=settings.OTP_EXPIRATION_SECONDS,
        )

        otp = OTPService.generate(
            OTP_REGISTER_PREFIX,
            email,
        )

        EmailService.send_otp_email(
            recipient_email=email,
            otp=otp,
        )