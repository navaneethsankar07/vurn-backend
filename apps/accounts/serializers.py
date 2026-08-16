from django.conf import settings
from rest_framework import serializers

from apps.organizations.models import Organization

from .models import User
from .validators import (
    optional_last_name_validator,
    validate_username,
    validate_user_password,
    first_name_regex_validator,
)
from .constants import ACCOUNT_DELETION_CONFIRMATION


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={"invalid": "Enter a valid email address."}
    )
    username = serializers.CharField(
        min_length=3,
        max_length=15,
        validators=[validate_username],
        error_messages={
            "min_length": "Username must be at least 3 characters.",
            "max_length": "Username cannot exceed 15 characters.",
        },
    )
    first_name = serializers.CharField(
        max_length=30,
        validators=[first_name_regex_validator],
        error_messages={
            "min_length": "First name must be at least 2 characters.",
            "blank": "First name is required.",
        },
    )
    last_name = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        validators=[optional_last_name_validator],
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_user_password],
        error_messages={
            "min_length": "Password must be at least 8 characters.",
        },
    )
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "Email address is required.",
            "invalid": "Invalid email address format.",
            "blank": "Email address cannot be empty.",
        }
    )


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

    class Meta:
        model = Organization
        fields = [
            "name",
            "slug",
            "icon",
            "logo_url"
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
