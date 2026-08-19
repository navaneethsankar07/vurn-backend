from rest_framework import serializers

from .models import OrganizationRole

from .constants import (
    ORGANIZATION_ACCENT_COLORS,
    ORGANIZATION_ICONS,
)


def validate_organization_icon(value: str) -> None:
    if value not in ORGANIZATION_ICONS:
        raise serializers.ValidationError("Invalid organization icon.")


def validate_organization_accent_color(
    value: str,
) -> None:
    if value not in ORGANIZATION_ACCENT_COLORS.values():
        raise serializers.ValidationError("Invalid organization accent color.")


def validate_organization_role_name(
    *,
    organization,
    name: str,
    role_id=None,
) -> None:
    queryset = OrganizationRole.objects.filter(
        organization=organization,
        name__iexact=name,
    )

    if role_id is not None:
        queryset = queryset.exclude(id=role_id)

    if queryset.exists():
        raise serializers.ValidationError("A role with this name already exists.")
