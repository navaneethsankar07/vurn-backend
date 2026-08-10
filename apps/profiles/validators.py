import re

from rest_framework import serializers

USERNAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9_.-]*[a-z0-9])?$")


def validate_first_name(value: str) -> str:
    value = value.strip()

    if not value:
        raise serializers.ValidationError("First name cannot be empty.")

    return value


def validate_last_name(value: str) -> str:
    return value.strip()


def validate_username(value: str) -> str:
    value = value.strip().lower()

    if not value:
        raise serializers.ValidationError("Username cannot be empty.")

    if not USERNAME_PATTERN.fullmatch(value):
        raise serializers.ValidationError(
            "Username can contain only letters, numbers, "
            "underscores, hyphens, and periods."
        )

    return value
