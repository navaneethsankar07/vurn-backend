from django.core.exceptions import ValidationError

from .constants import (
    ORGANIZATION_ACCENT_COLORS,
    ORGANIZATION_ICONS,
)


def validate_organization_icon(value: str) -> None:
    if value not in ORGANIZATION_ICONS:
        raise ValidationError("Invalid organization icon.")


def validate_organization_accent_color(
    value: str,
) -> None:
    if value not in ORGANIZATION_ACCENT_COLORS:
        raise ValidationError("Invalid organization accent color.")
