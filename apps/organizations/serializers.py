from rest_framework import serializers

from apps.organizations.constants import MOCK_ORGANIZATION_STATS

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


class OrganizationListSerializer(
    serializers.ModelSerializer,
):
    role = serializers.SerializerMethodField()

    member_count = serializers.SerializerMethodField()

    project_count = serializers.SerializerMethodField()

    last_opened_at = serializers.SerializerMethodField()

    is_pinned = serializers.SerializerMethodField()

    class Meta:
        model = Organization

        fields = [
            "id",
            "name",
            "description",
            "slug",
            "icon",
            "accent_color",
            "logo_url",
            "role",
            "member_count",
            "project_count",
            "last_opened_at",
            "is_pinned",
        ]

    def get_role(
        self,
        obj,
    ):
        return "owner"

    def get_member_count(
        self,
        obj,
    ):
        stats = MOCK_ORGANIZATION_STATS.get(
            obj.id,
            {
                "member_count": 1,
                "project_count": 0,
            },
        )

        return stats["member_count"]

    def get_project_count(
        self,
        obj,
    ):
        stats = MOCK_ORGANIZATION_STATS.get(
            obj.id,
            {
                "member_count": 1,
                "project_count": 0,
            },
        )

        return stats["project_count"]

    def get_last_opened_at(
        self,
        obj,
    ):
        return None

    def get_is_pinned(
        self,
        obj,
    ):
        return False