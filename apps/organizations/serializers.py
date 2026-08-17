from rest_framework import serializers

from apps.organizations.constants import (
    LOGO_ALLOWED_TYPES,
    LOGO_MAX_SIZE,
    MOCK_ORGANIZATION_STATS,
)

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


class OrganizationDashboardSerializer(
    serializers.Serializer,
):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    slug = serializers.CharField()
    icon = serializers.CharField()
    logo_url = serializers.URLField(
        allow_null=True,
    )
    accent_color = serializers.CharField()
    updated_at = serializers.DateTimeField()
    total_projects = serializers.IntegerField()
    total_members = serializers.IntegerField()
    active_sprints = serializers.IntegerField()
    open_issues = serializers.IntegerField()
    completed_issues = serializers.IntegerField()


class UpdateOrganizationSettingsSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Organization
        fields = [
            "name",
            "slug",
            "description",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Organization name cannot be empty.")

        return value

    def validate_slug(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError("Organization slug cannot be empty.")

        organization = self.instance

        if (
            Organization.objects.filter(
                slug=value,
            )
            .exclude(
                id=organization.id,
            )
            .exists()
        ):
            raise serializers.ValidationError("Organization slug is already taken.")

        return value

    def validate_description(self, value):
        return value.strip()


class UpdateOrganizationBrandingSerializer(
    serializers.Serializer,
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

    logo = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    def validate_logo(self, value):
        if value is None:
            return value

        if value.size > LOGO_MAX_SIZE:
            raise serializers.ValidationError("Organization logo must not exceed 5 MB.")

        if value.content_type not in LOGO_ALLOWED_TYPES:
            raise serializers.ValidationError(
                "Organization logo must be a JPEG, PNG, or WebP image."
            )

        return value


class OrganizationDeleteRequestSerializer(
    serializers.Serializer,
):
    name = serializers.CharField(
        required=True,
    )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Organization name is required.")

        return value


class OrganizationDeleteConfirmSerializer(
    serializers.Serializer,
):
    otp = serializers.RegexField(
        regex=r"^\d{6}$",
        error_messages={
            "invalid": "OTP must be exactly 6 digits.",
        },
    )
