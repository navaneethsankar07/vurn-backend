from rest_framework import serializers

from .models import Organization
from .validators import (
    validate_organization_accent_color,
    validate_organization_icon,
)


class CreateOrganizationSerializer(
    serializers.ModelSerializer,
):
    icon = serializers.CharField(
        required=False,
        validators=[
            validate_organization_icon,
        ],
    )

    accent_color = serializers.CharField(
        required=False,
        validators=[
            validate_organization_accent_color,
        ],
    )

    class Meta:
        model = Organization

        fields = [
            "name",
            "description",
            "slug",
            "icon",
            "accent_color",
        ]

        extra_kwargs = {
            "slug": {
                "required": True,
            },
            "description": {
                "required": False,
                "allow_blank": True,
            },
        }

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Organization name is required.")

        return value

    def validate_slug(self, value):
        value = value.strip().lower()

        if Organization.objects.filter(
            slug=value,
        ).exists():
            raise serializers.ValidationError("Organization slug is already taken.")

        return value
