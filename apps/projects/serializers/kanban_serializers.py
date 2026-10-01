from rest_framework import serializers

from ..constants import ISSUE_PRIORITY_CHOICES, ISSUE_TYPE_CHOICES, KANBAN_SORT_CHOICES

from ..models import Sprint


class KanbanIssueQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    sprint_id = serializers.IntegerField(required=False, min_value=1)
    parent_id = serializers.IntegerField(required=False, min_value=1)
    issue_type = serializers.ChoiceField(choices=ISSUE_TYPE_CHOICES, required=False)
    assignee_id = serializers.IntegerField(required=False, min_value=1)
    priority = serializers.ChoiceField(choices=ISSUE_PRIORITY_CHOICES, required=False)
    sort = serializers.ChoiceField(
        choices=[choice[0] for choice in KANBAN_SORT_CHOICES],
        required=False,
        default="position",
    )


class KanbanIssueStatusSerializer(serializers.Serializer):
    status_id = serializers.IntegerField(min_value=1)


class KanbanIssuePositionSerializer(serializers.Serializer):
    position = serializers.IntegerField(min_value=0)


class KanbanIssueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField()
    title = serializers.CharField()
    issue_type = serializers.CharField()
    status_id = serializers.IntegerField()
    sprint_id = serializers.IntegerField(allow_null=True)
    story_points = serializers.IntegerField(allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    estimated_time = serializers.IntegerField(allow_null=True)
    priority = serializers.CharField()
    assignee_id = serializers.IntegerField(allow_null=True)
    position = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class KanbanSprintFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ["id", "name", "status"]
