import hashlib
import hmac
import secrets
import string

from django.conf import settings
from django.core.cache import cache


class OTPService:
    @classmethod
    def _generate_otp(cls) -> str:
        return "".join(
            secrets.choice(string.digits)
            for _ in range(settings.OTP_LENGTH)
        )

    @classmethod
    def _hash(cls, otp: str) -> str:
        return hashlib.sha256(otp.encode()).hexdigest()

    @classmethod
    def _key(cls, prefix: str, identifier: str) -> str:
        return f"{prefix}:{identifier.strip().lower()}"

    @classmethod
    def generate(
        cls,
        prefix: str,
        identifier: str,
    ) -> str:
        otp = cls._generate_otp()

        cache.set(
            cls._key(prefix, identifier),
            cls._hash(otp),
            timeout=settings.OTP_EXPIRATION_SECONDS,
        )

        return otp

    @classmethod
    def verify(
        cls,
        prefix: str,
        identifier: str,
        otp: str,
    ) -> bool:
        cached_otp_hash = cache.get(
            cls._key(prefix, identifier)
        )

        if cached_otp_hash is None:
            return False

        entered_hash = cls._hash(otp)

        if not hmac.compare_digest(
            cached_otp_hash,
            entered_hash,
        ):
            return False

        cache.delete(
            cls._key(prefix, identifier)
        )

        return True

    @classmethod
    def delete(
        cls,
        prefix: str,
        identifier: str,
    ) -> None:
        cache.delete(
            cls._key(prefix, identifier)
        )