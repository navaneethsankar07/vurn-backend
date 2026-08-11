from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.models import User

from .validators import (
    validate_first_name,
    validate_last_name,
    validate_username,
)
from .constants import AVATAR_ALLOWED_TYPES, AVATAR_MAX_SIZE


class ProfileUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "username",
            "email",
            "avatar",
            "created_at",
            "last_login",
        ]
        read_only_fields = fields


class ProfileStatisticsSerializer(serializers.Serializer):
    organizations_joined = serializers.IntegerField()
    projects = serializers.IntegerField()
    assigned_issues = serializers.IntegerField()
    completed_issues = serializers.IntegerField()
    comments = serializers.IntegerField()
    github_linked_projects = serializers.IntegerField()


class RecentActivitySerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()


class ProfileSerializer(serializers.Serializer):
    user = ProfileUserSerializer()
    statistics = ProfileStatisticsSerializer()
    recent_activity = RecentActivitySerializer(
        many=True,
    )


class UpdateProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        validators=[validate_first_name],
    )

    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[validate_last_name],
    )

    username = serializers.CharField(
        validators=[validate_username],
    )

    avatar = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "avatar",
        ]

    def validate_username(self, value):
        if (
            User.objects.filter(
                username=value,
            )
            .exclude(
                id=self.instance.id,
            )
            .exists()
        ):
            raise serializers.ValidationError("Username is already taken.")

        return value

    def validate_avatar(self, value):
        if value is None:
            return value

        if value.size > AVATAR_MAX_SIZE:
            raise serializers.ValidationError("Avatar image must not exceed 5 MB.")

        allowed_types = AVATAR_ALLOWED_TYPES

        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Avatar must be a JPEG, PNG, or WebP image."
            )

        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        trim_whitespace=False,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {
                    "new_password": (
                        "New password must be different from " "the current password."
                    )
                }
            )

        return attrs
