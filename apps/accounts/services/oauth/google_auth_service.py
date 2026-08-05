from django.conf import settings
from django.db import transaction
from django.utils import timezone

from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token

from apps.accounts.exceptions import InvalidGoogleTokenException
from apps.accounts.models import SocialAccount, User
from apps.accounts.services.token_service import TokenService


class GoogleAuthService:

    @classmethod
    @transaction.atomic
    def authenticate(
        cls,
        google_id_token: str,
    ) -> dict:

        google_user = cls._verify_id_token(
            google_id_token,
        )

        user = cls._get_or_create_user(
            google_user,
        )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        tokens = TokenService.generate_tokens(user)

        return {
            "user": user,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }

    @staticmethod
    def _verify_id_token(
        google_id_token: str,
    ) -> dict:

        try:
            google_user = id_token.verify_oauth2_token(
                google_id_token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )

        except (GoogleAuthError, ValueError) as exc:
            raise InvalidGoogleTokenException("Invalid Google ID token.") from exc

        if not google_user.get("email_verified", False):
            raise InvalidGoogleTokenException("Google email is not verified.")

        return google_user

    @classmethod
    def _get_or_create_user(
        cls,
        google_user: dict,
    ) -> User:

        email = google_user["email"].strip().lower()

        social_account = (
            SocialAccount.objects.filter(
                provider=SocialAccount.Provider.GOOGLE,
                provider_user_id=google_user["sub"],
            )
            .select_related("user")
            .first()
        )

        if social_account:
            return social_account.user

        user = User.objects.filter(
            email=email,
        ).first()

        if user is None:

            user = User.objects.create_user(
                email=email,
                username=cls._generate_username(email),
                first_name=google_user.get("given_name", ""),
                last_name=google_user.get("family_name", ""),
                password=None,
                is_email_verified=True,
            )

        SocialAccount.objects.get_or_create(
            provider=SocialAccount.Provider.GOOGLE,
            provider_user_id=google_user["sub"],
            defaults={
                "user": user,
                "provider_email": email,
                "provider_display_name": google_user.get("name", ""),
                "avatar_url": google_user.get("picture", ""),
            },
        )

        return user

    @staticmethod
    def _generate_username(
        email: str,
    ) -> str:

        base = email.split("@")[0]

        username = base

        counter = 1

        while User.objects.filter(
            username=username,
        ).exists():

            username = f"{base}{counter}"
            counter += 1

        return username
