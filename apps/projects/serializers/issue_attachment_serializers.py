from rest_framework import serializers

from ..constants import ALLOWED_ATTACHMENT_MIME_TYPES, MAX_ATTACHMENT_SIZE

from ..models import Attachment


class AttachmentUploadSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    file_size = serializers.IntegerField(min_value=1, max_value=MAX_ATTACHMENT_SIZE)
    mime_type = serializers.CharField(max_length=100)

    def validate_file_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("File name cannot be empty.")

        return value

    def validate_mime_type(self, value):
        value = value.strip().lower()

        if value not in ALLOWED_ATTACHMENT_MIME_TYPES:
            raise serializers.ValidationError("This file type is not supported.")

        return value


class AttachmentUploadCompleteSerializer(serializers.Serializer):
    object_key = serializers.CharField(max_length=500)

    def validate_object_key(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Object key cannot be empty.")

        return value


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_id = serializers.IntegerField(source="uploaded_by.id", read_only=True)
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name", read_only=True
    )
    uploaded_by_avatar = serializers.URLField(
        source="uploaded_by.avatar", read_only=True, allow_null=True
    )
    download_url = serializers.URLField(read_only=True)

    class Meta:
        model = Attachment
        fields = [
            "id",
            "file_name",
            "file_size",
            "mime_type",
            "uploaded_by_id",
            "uploaded_by_name",
            "uploaded_by_avatar",
            "created_at",
            "download_url",
        ]
