import time

import jwt
import requests
from django.conf import settings

from ...exceptions import GitAuthenticationException


class GitHubAuthenticationService:

    @staticmethod
    def generate_app_jwt() -> str:
        now = int(time.time())

        payload = {"iat": now - 60, "exp": now + 540, "iss": settings.GITHUB_APP_ID}

        private_key_path = settings.BASE_DIR / settings.GITHUB_PRIVATE_KEY_PATH
        try:
            with private_key_path.open("rb") as pem_file:
                private_key = pem_file.read()

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
