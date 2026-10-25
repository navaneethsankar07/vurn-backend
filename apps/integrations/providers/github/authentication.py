import os
from pathlib import Path
import time

import jwt
import requests
from django.conf import settings

from ...exceptions import GitAuthenticationException


def get_github_private_key() -> bytes:
    raw_key = os.getenv("GITHUB_PRIVATE_KEY")
    if raw_key:
        return raw_key.replace("\\n", "\n").encode("utf-8")

    key_setting = getattr(settings, "GITHUB_PRIVATE_KEY_PATH", None) or os.getenv(
        "GITHUB_PRIVATE_KEY_PATH"
    )
    if key_setting:
        path = Path(key_setting)
        if not path.is_absolute():
            path = settings.BASE_DIR / path
        if path.exists():
            with path.open("rb") as f:
                return f.read()

    raise ValueError("GitHub private key not found in environment or file path.")


class GitHubAuthenticationService:

    @staticmethod
    def generate_app_jwt() -> str:
        now = int(time.time())

        payload = {"iat": now - 60, "exp": now + 540, "iss": settings.GITHUB_APP_ID}

        try:
            private_key = get_github_private_key()
            return jwt.encode(payload, private_key, algorithm="RS256")
        except Exception as exc:
            raise GitAuthenticationException(
                "Unable to generate GitHub App token."
            ) from exc

    @staticmethod
    def generate_installation_token(*, installation_id) -> str:
        app_jwt = GitHubAuthenticationService.generate_app_jwt()

        response = requests.post(
            f"https://api.github.com/app/installations/"
            f"{installation_id}/access_tokens",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {app_jwt}",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            timeout=15,
        )

        if not response.ok:
            raise GitAuthenticationException(
                "Unable to generate GitHub installation token."
            )

        data = response.json()
        token = data.get("token")

        if not token:
            raise GitAuthenticationException(
                "GitHub did not return an installation token."
            )

        return token

    @staticmethod
    def get_installation_details(*, installation_id):
        app_jwt = GitHubAuthenticationService.generate_app_jwt()

        response = requests.get(
            f"https://api.github.com/app/installations/{installation_id}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {app_jwt}",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            timeout=15,
        )

        if not response.ok:
            raise GitAuthenticationException(
                "Unable to validate GitHub App installation."
            )

        data = response.json()
        account = data.get("account") or {}

        return {
            "installation_id": data.get("id"),
            "account_login": account.get("login"),
            "account_type": account.get("type"),
        }
