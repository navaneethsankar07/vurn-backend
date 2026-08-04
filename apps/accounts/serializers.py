from rest_framework import serializers
from django.conf import settings
from apps.accounts.validators import (
    validate_username,
    validate_user_password,
)


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
        min_length=settings.OTP_LENGTH, max_length=settings.OTP_LENGTH
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
    )
