import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password

username_regex_validator = RegexValidator(
    regex=r"^[a-z0-9_.]{3,15}$",
    message="Username must be 3-15 characters long and contain only lowercase letters, numbers, underscores, and periods.",
)

first_name_regex_validator = RegexValidator(
    regex=r"^[a-zA-Z]+$",
    message="First name can only contain letters.",
)

_last_name_regex = RegexValidator(
    regex=r"^[a-zA-Z]+$",
    message="Last name can only contain letters.",
)

password_complexity_validator = RegexValidator(
    regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])",
    message="Must include uppercase, lowercase, number, and special character.",
)


def optional_last_name_validator(value: str):
    if value and value.strip():
        _last_name_regex(value)

def validate_username(username: str) -> str:
    username = username.strip().lower()
    username_regex_validator(username)
    return username


def validate_user_password(password: str) -> str:
    password_complexity_validator(password)
    validate_password(password)
    return password