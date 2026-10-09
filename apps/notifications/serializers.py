from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, allow_null=True
    )
    project_name = serializers.CharField(
        source="project.name", read_only=True, allow_null=True
    )
    issue_key = serializers.CharField(
        source="issue.key", read_only=True, allow_null=True
    )
    sprint_name = serializers.CharField(
        source="sprint.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "organization",
            "organization_name",
            "invitation",
            "project",
            "project_name",
            "issue",
            "issue_key",
            "sprint",
            "sprint_name",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields
