from django.conf import settings
from rest_framework import serializers

from apps.organizations.models import Organization

from .models import User
from .validators import (
    validate_username,
    validate_user_password,
)
from .constants import ACCOUNT_DELETION_CONFIRMATION


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=15, validators=[validate_username])
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True, validators=[validate_user_password]
    )
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()

    otp = serializers.CharField(
        min_length=settings.OTP_LENGTH,
        max_length=settings.OTP_LENGTH,
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
    )


class UserOrganizationSerializer(serializers.ModelSerializer):
    """Minimal organization serializer for the user payload."""

    class Meta:
        model = Organization
        fields = [
            "name",
            "slug",
        ]
        read_only_fields = fields


class CurrentUserSerializer(serializers.ModelSerializer):
    organizations = UserOrganizationSerializer(
        source="owned_organizations",
        many=True,
        read_only=True,
    )

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "full_name",
            "avatar",
            "organizations",
        ]

        read_only_fields = fields


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs


class RequestAccountDeletionSerializer(serializers.Serializer):
    confirmation = serializers.CharField(
        trim_whitespace=True,
    )

    def validate_confirmation(self, value):
        if value != ACCOUNT_DELETION_CONFIRMATION:
            raise serializers.ValidationError("Invalid account deletion confirmation.")

        return value


class ConfirmAccountDeletionSerializer(serializers.Serializer):
    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        trim_whitespace=True,
    )
