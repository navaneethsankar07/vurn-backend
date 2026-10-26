import hashlib
import secrets

from django.conf import settings
from django.db import transaction
from django.core.cache import cache

from apps.accounts.models import User
from apps.accounts.constants import PASSWORD_RESET_PREFIX
from apps.shared.services.email_service import EmailService
from apps.accounts.exceptions import (
    InvalidPasswordResetTokenException,
)


class PasswordResetService:

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def _key(
        cls,
        token: str,
    ) -> str:
        return f"{PASSWORD_RESET_PREFIX}:" f"{cls._hash(token)}"

    @classmethod
    def send_reset_link(
        cls,
        email: str,
    ) -> None:

        email = email.strip().lower()

        user = User.objects.filter(
            email=email,
            is_active=True,
        ).first()

        if user is None:
            return

        token = secrets.token_urlsafe(32)

        cache.set(
            cls._key(token),
            user.id,
            timeout=settings.PASSWORD_RESET_EXPIRATION_SECONDS,
        )

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        EmailService.send_password_reset_email(
            recipient_email=user.email,
            reset_link=reset_link,
        )

    @classmethod
    @transaction.atomic
    def reset_password(
        cls,
        token: str,
        password: str,
    ) -> None:

        user_id = cache.get(cls._key(token))

        if user_id is None:
            raise InvalidPasswordResetTokenException(
                "Invalid or expired password reset link."
            )

        user = User.objects.get(id=user_id)

        user.set_password(password)

        user.save(update_fields=["password"])

        cache.delete(cls._key(token))
