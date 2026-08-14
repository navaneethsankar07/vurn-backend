import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password

username_regex_validator = RegexValidator(
    regex=r"^[a-z0-9_.]+$",
    message="Only lowercase letters, numbers, underscores, and periods are allowed.",
)

first_name_regex_validator = RegexValidator(
    regex=r"^[a-zA-Z]+$",
    message="First name can only contain letters.",
)

_last_name_regex = RegexValidator(
    regex=r"^[a-zA-Z]+$",
    message="Last name can only contain letters.",
)


def optional_last_name_validator(value: str):
    if value and value.strip():
        _last_name_regex(value)

def validate_username(username: str) -> str:
    username = username.strip().lower()
    username_regex_validator(username)
    return username


def validate_user_password(password: str) -> str:
    validate_password(password)
    return password