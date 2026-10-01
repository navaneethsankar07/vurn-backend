import re
from rest_framework import serializers

from ..constants import STATUS_CATEGORY_CHOICES

from ..models import WorkflowStatus


class WorkflowStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStatus
        fields = [
            "id",
            "name",
            "category",
            "color",
            "icon",
            "position",
            "is_default",
            "is_archived",
            "allow_from_backlog",
            "allow_incoming",
            "allow_outgoing",
        ]


class WorkflowTransitionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    from_status_id = serializers.IntegerField()
    to_status_id = serializers.IntegerField()
    name = serializers.CharField()


class WorkflowOverviewSerializer(serializers.Serializer):
    statuses = WorkflowStatusSerializer(many=True)
    transitions = WorkflowTransitionSerializer(many=True)


class WorkflowStatusCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=60)
    category = serializers.ChoiceField(choices=STATUS_CATEGORY_CHOICES)
    color = serializers.CharField(max_length=7)
    icon = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True
    )
    position = serializers.IntegerField(min_value=0)
    is_default = serializers.BooleanField(required=False, default=False)
    allow_from_backlog = serializers.BooleanField(required=False, default=True)
    allow_incoming = serializers.BooleanField(required=False, default=True)
    allow_outgoing = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Status name cannot be empty.")

        return value

    def validate_color(self, value):
        value = value.strip().upper()

        if not re.fullmatch(r"#[0-9A-F]{6}", value):
            raise serializers.ValidationError("Enter a valid hex color.")

        return value


class WorkflowStatusUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=60, required=False)
    category = serializers.ChoiceField(choices=STATUS_CATEGORY_CHOICES, required=False)
    color = serializers.CharField(max_length=7, required=False)
    icon = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True
    )
    position = serializers.IntegerField(min_value=0, required=False)
    is_default = serializers.BooleanField(required=False)
    is_archived = serializers.BooleanField(required=False)
    allow_from_backlog = serializers.BooleanField(required=False)
    allow_incoming = serializers.BooleanField(required=False)
    allow_outgoing = serializers.BooleanField(required=False)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Status name cannot be empty.")

        return value

    def validate_color(self, value):
        value = value.strip().upper()

        if not re.fullmatch(r"#[0-9A-F]{6}", value):
            raise serializers.ValidationError("Enter a valid hex color.")

        return value


class WorkflowTransitionCreateSerializer(serializers.Serializer):
    from_status_id = serializers.IntegerField()
    to_status_id = serializers.IntegerField()
    name = serializers.CharField(max_length=60, required=False, allow_blank=True)


class WorkflowTransitionUpdateSerializer(serializers.Serializer):
    from_status_id = serializers.IntegerField()
    to_status_id = serializers.IntegerField()
    name = serializers.CharField(max_length=60, required=False, allow_blank=True)


class WorkflowStatusPositionSerializer(serializers.Serializer):
    position = serializers.IntegerField(min_value=0)
