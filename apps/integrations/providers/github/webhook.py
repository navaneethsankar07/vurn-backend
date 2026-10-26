import hashlib
import hmac

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def verify_github_webhook_signature(*, payload, signature):
    secret = settings.GITHUB_WEBHOOK_SECRET

    if not secret:
        raise ImproperlyConfigured("GITHUB_WEBHOOK_SECRET is not configured.")

    if not signature or not signature.startswith("sha256="):
        return False

    expected_signature = (
        "sha256="
        + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    )

    return hmac.compare_digest(expected_signature, signature)
