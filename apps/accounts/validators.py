import re

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


USERNAME_REGEX = re.compile(r"^[a-z0-9_.]{3,15}$")


def validate_username(username: str) -> str:
    username = username.strip().lower()

    if not USERNAME_REGEX.fullmatch(username):
        raise ValidationError(
            "Username must be 3-15 characters long and contain only lowercase letters, numbers, underscores, and periods."
        )

    return username


def validate_user_password(password: str) -> str:
    validate_password(password)
    return password