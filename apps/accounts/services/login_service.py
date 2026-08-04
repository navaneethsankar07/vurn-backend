from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.exceptions import (
    EmailNotVerifiedException,
    InactiveAccountException,
    InvalidCredentialsException,
)
from apps.accounts.models import User


class LoginService:

    @staticmethod
    def _generate_tokens(user: User) -> dict:
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


    @classmethod
    @transaction.atomic
    def login(
        cls,
        email: str,
        password: str,
    ) -> dict:

        user = authenticate(
            email=email.strip().lower(),
            password=password,
        )

        if user is None:
            raise InvalidCredentialsException(
                "Invalid email or password."
            )

        if not user.is_email_verified:
            raise EmailNotVerifiedException(
                "Please verify your email first."
            )

        if not user.is_active:
            raise InactiveAccountException(
                "Your account has been deactivated."
            )

        user.last_login = timezone.now()

        user.save(
            update_fields=["last_login"]
        )

        tokens = cls._generate_tokens(user)

        return {
            "user": user,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }