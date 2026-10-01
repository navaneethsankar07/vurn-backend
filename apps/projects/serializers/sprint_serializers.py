from rest_framework import serializers

from ..constants import SPRINT_STATUS_CHOICES

from ..models import Sprint


class SprintSerializer(serializers.ModelSerializer):
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = Sprint
        fields = [
            "id",
            "name",
            "goal",
            "description",
            "start_date",
            "end_date",
            "estimated_days",
            "status",
            "created_by_id",
            "created_by_name",
            "created_at",
            "updated_at",
        ]


class SprintListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=SPRINT_STATUS_CHOICES, required=False)
    sort = serializers.ChoiceField(
        choices=[
            "name_asc",
            "name_desc",
            "start_date_asc",
            "start_date_desc",
            "end_date_asc",
            "end_date_desc",
            "created_asc",
            "created_desc",
        ],
        required=False,
        default="created_desc",
    )


class SprintCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    goal = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    estimated_days = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Sprint name cannot be empty.")

        return value

    def validate(self, attrs):
        end_date = attrs.get("end_date")
        estimated_days = attrs.get("estimated_days")

        if end_date is None and estimated_days is None:
            raise serializers.ValidationError(
                "Either end date or estimated days is required."
            )
        if end_date is not None and estimated_days is not None:
            raise serializers.ValidationError(
                "Provide either end date or estimated days."
            )
        if end_date is not None:
            if attrs["start_date"] > end_date:
                raise serializers.ValidationError(
                    {"end_date": ("End date must be after the start date.")}
                )

        return attrs


class SprintUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=False)
    goal = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False, allow_null=True)
    estimated_days = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Sprint name cannot be empty.")

        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        estimated_days = attrs.get("estimated_days")

        if end_date is not None and estimated_days is not None:
            raise serializers.ValidationError(
                "Provide either end date or estimated days."
            )

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError(
                    {
                        "end_date": (
                            "End date must be after or equal " "to the start date."
                        )
                    }
                )

        return attrs


class SprintCompletionIssueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField()
    title = serializers.CharField()
    issue_type = serializers.CharField()
    status_id = serializers.IntegerField(source="status.id")
    status_name = serializers.CharField(source="status.name")
    parent_id = serializers.IntegerField(allow_null=True)
    parent_key = serializers.CharField(source="parent.key", allow_null=True)


class SprintCompleteSerializer(serializers.Serializer):
    incomplete_issue_action = serializers.ChoiceField(
        choices=(
            ("sprint", "Move to Sprint"),
            ("new_sprint", "Create New Sprint"),
            ("backlog", "Move to Backlog"),
        ),
        required=False,
    )
    target_sprint_id = serializers.IntegerField(required=False, min_value=1)

    def validate(self, attrs):
        action = attrs.get("incomplete_issue_action")
        target_sprint_id = attrs.get("target_sprint_id")

        if action == "sprint" and target_sprint_id is None:
            raise serializers.ValidationError(
                {"target_sprint_id": ("Target sprint is required.")}
            )

        if action != "sprint" and target_sprint_id is not None:
            raise serializers.ValidationError(
                {
                    "target_sprint_id": (
                        "Target sprint is only allowed "
                        "when moving issues to another sprint."
                    )
                }
            )

        return attrs
