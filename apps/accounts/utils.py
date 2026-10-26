from django.conf import settings
from rest_framework.response import Response


def set_auth_cookie(response: Response, refresh_token: str) -> None:

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path="/api/v1/auth/",
        domain=getattr(settings, "SESSION_COOKIE_DOMAIN", None),
    )


def delete_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth/",
        domain=getattr(settings, "SESSION_COOKIE_DOMAIN", None),
        samesite="Lax",
    )
