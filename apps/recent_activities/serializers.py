from rest_framework import serializers

from .models import RecentActivity


class RecentActivitySerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    project_name = serializers.CharField(
        source="project.name", read_only=True, default=None
    )
    sprint_name = serializers.CharField(
        source="sprint.name", read_only=True, default=None
    )
    issue_key = serializers.CharField(source="issue.key", read_only=True, default=None)

    class Meta:
        model = RecentActivity
        fields = [
            "id",
            "activity_type",
            "description",
            "actor",
            "project_name",
            "sprint_name",
            "issue_key",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields

    def get_actor(self, obj):
        if obj.actor is None:
            return None

        return {"id": obj.actor_id, "username": obj.actor.full_name}
