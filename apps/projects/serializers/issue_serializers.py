from rest_framework import serializers

from .issue_label_serializers import LabelSerializer

from ..constants import ISSUE_PRIORITY_CHOICES, ISSUE_SORT_CHOICES, ISSUE_TYPE_CHOICES

from ..models import Issue, IssueSprintHistory, Sprint


class IssueCreateSerializer(serializers.Serializer):
    issue_type = serializers.ChoiceField(choices=ISSUE_TYPE_CHOICES)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    sprint_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_time = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    status_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    assignee_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    priority = serializers.ChoiceField(
        choices=ISSUE_PRIORITY_CHOICES, required=False, default="medium"
    )
    story_points = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Issue title cannot be empty.")

        return value


class IssueListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    issue_type = serializers.ChoiceField(choices=ISSUE_TYPE_CHOICES, required=False)
    parent_id = serializers.IntegerField(required=False, min_value=1)
    epic_id = serializers.IntegerField(required=False, min_value=1)
    story_id = serializers.IntegerField(required=False, min_value=1)
    sprint_id = serializers.IntegerField(required=False, min_value=1)
    assignee_id = serializers.IntegerField(required=False, min_value=1)
    priority = serializers.ChoiceField(choices=ISSUE_PRIORITY_CHOICES, required=False)
    status_id = serializers.IntegerField(required=False, min_value=1)
    sort = serializers.ChoiceField(
        choices=[choice[0] for choice in ISSUE_SORT_CHOICES],
        required=False,
        default="position",
    )


class IssueSprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ["id", "name", "status", "start_date", "end_date"]


class IssueResponseSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)
    project_id = serializers.IntegerField(source="project.id", read_only=True)
    parent_key = serializers.CharField(
        source="parent.key", read_only=True, allow_null=True
    )
    parent_id = serializers.IntegerField(
        source="parent.id", read_only=True, allow_null=True
    )
    sprint_id = serializers.IntegerField(
        source="sprint.id", read_only=True, allow_null=True
    )
    sprint_name = serializers.CharField(
        source="sprint.name", read_only=True, allow_null=True
    )
    sprint = IssueSprintSerializer(read_only=True, allow_null=True)
    status_id = serializers.IntegerField(source="status.id", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)
    assignee_id = serializers.IntegerField(
        source="assignee.id", read_only=True, allow_null=True
    )
    assignee_name = serializers.CharField(
        source="assignee.full_name", read_only=True, allow_null=True
    )
    reporter_name = serializers.CharField(source="reporter.full_name", read_only=True)
    labels = LabelSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "key",
            "project_id",
            "parent_key",
            "parent_id",
            "sprint_id",
            "sprint_name",
            "sprint",
            "status_id",
            "due_date",
            "estimated_time",
            "status_name",
            "assignee_id",
            "assignee_name",
            "reporter_name",
            "issue_number",
            "issue_type",
            "title",
            "description",
            "priority",
            "story_points",
            "position",
            "labels",
            "created_at",
            "updated_at",
        ]


class IssueUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    sprint_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    status_id = serializers.IntegerField(required=False, min_value=1)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_time = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    assignee_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    priority = serializers.ChoiceField(choices=ISSUE_PRIORITY_CHOICES, required=False)
    story_points = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Issue title cannot be empty.")

        return value


class SubtaskListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    sort = serializers.ChoiceField(
        choices=[
            "position",
            "created_asc",
            "created_desc",
            "updated_asc",
            "updated_desc",
        ],
        required=False,
        default="position",
    )


class IssueSprintHistorySerializer(serializers.ModelSerializer):
    sprint_id = serializers.IntegerField(
        source="sprint.id", read_only=True, allow_null=True
    )
    sprint_name = serializers.SerializerMethodField()

    class Meta:
        model = IssueSprintHistory
        fields = ["sprint_id", "sprint_name", "moved_at"]

    def get_sprint_name(self, obj):
        if obj.sprint is None:
            return "Backlog"

        return obj.sprint.name
