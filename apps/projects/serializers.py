import re

from rest_framework import serializers

from .constants import PROJECT_ICONS


class ProjectCreateSerializer(
    serializers.Serializer,
):

    name = serializers.CharField(
        max_length=150,
    )

    key = serializers.CharField(
        max_length=10,
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    icon = serializers.ChoiceField(
        choices=PROJECT_ICONS,
        required=False,
        default="hexagon",
    )

    accent_color = serializers.CharField(
        max_length=7,
        required=False,
        default="#F59E0B",
    )

    start_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    target_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    def validate_name(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Project name cannot be empty.")

        return value

    def validate_key(
        self,
        value,
    ):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Project key cannot be empty.")

        if not re.fullmatch(
            r"[A-Z][A-Z0-9]*",
            value,
        ):
            raise serializers.ValidationError(
                "Project key must start with a letter and contain "
                "only uppercase letters and numbers."
            )

        return value

    def validate_accent_color(
        self,
        value,
    ):
        value = value.strip().upper()

        if not re.fullmatch(
            r"#[0-9A-F]{6}",
            value,
        ):
            raise serializers.ValidationError("Enter a valid hex color.")

        return value

    def validate(
        self,
        attrs,
    ):
        start_date = attrs.get(
            "start_date",
        )

        target_date = attrs.get(
            "target_date",
        )

        if start_date and target_date and target_date < start_date:
            raise serializers.ValidationError(
                {
                    "target_date": ("Target date cannot be before " "the start date."),
                }
            )

        return attrs


class ProjectCreateResponseSerializer(
    serializers.Serializer,
):
    id = serializers.IntegerField()
    name = serializers.CharField()
    key = serializers.CharField()
    slug = serializers.SlugField()
    description = serializers.CharField()
    icon = serializers.CharField()
    accent_color = serializers.CharField()
    logo_url = serializers.URLField(
        allow_null=True,
    )
    status = serializers.CharField()
    start_date = serializers.DateField(
        allow_null=True,
    )
    target_date = serializers.DateField(
        allow_null=True,
    )
    owner_id = serializers.IntegerField()
    project_lead_id = serializers.IntegerField()
    created_by_id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
