from rest_framework import serializers

from .constants import STORY_POINT_VALUES


class TaskBreakdownRequestSerializer(serializers.Serializer):
    issue_title = serializers.CharField(max_length=255)
    issue_description = serializers.CharField(
        required=False, allow_blank=True, max_length=10000
    )


class SuggestedSubtaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, max_length=3000)


class TaskBreakdownResponseSerializer(serializers.Serializer):
    summary = serializers.CharField(max_length=1000)
    subtasks = SuggestedSubtaskSerializer(many=True)


class StoryPointEstimationResponseSerializer(serializers.Serializer):
    estimated_story_points = serializers.IntegerField()
    rationale = serializers.CharField(max_length=1500)
    assumptions = serializers.ListField(
        child=serializers.CharField(max_length=300), max_length=5
    )
    confidence = serializers.ChoiceField(choices=("low", "medium", "high"))

    def validate_estimated_story_points(self, value):
        if value not in STORY_POINT_VALUES:
            raise serializers.ValidationError(
                "Estimated story points must be one of: 1, 2, 3, 5, 8, or 13."
            )

        return value


class StoryPointEstimationRequestSerializer(serializers.Serializer):
    issue_id = serializers.IntegerField(min_value=1)


class DuplicateDetectionRequestSerializer(serializers.Serializer):
    organization_slug = serializers.SlugField(max_length=255)
    project_slug = serializers.SlugField(max_length=255)
    title = serializers.CharField(max_length=255, trim_whitespace=True)
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=10000
    )
    issue_type = serializers.CharField(max_length=20, required=False)
    priority = serializers.CharField(max_length=20, required=False)

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")

        return value.strip()


class AIDuplicateCandidateSerializer(serializers.Serializer):
    issue_key = serializers.CharField(max_length=100)
    reason = serializers.CharField(max_length=1000)
    confidence = serializers.ChoiceField(choices=("low", "medium", "high"))


class AIDuplicateDetectionResponseSerializer(serializers.Serializer):
    duplicates = AIDuplicateCandidateSerializer(many=True, max_length=5)


class DuplicateIssueResultSerializer(serializers.Serializer):
    issue_id = serializers.IntegerField()
    key = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=255)
    reason = serializers.CharField(max_length=1000)
    confidence = serializers.ChoiceField(choices=("low", "medium", "high"))


class SprintSummaryRequestSerializer(serializers.Serializer):
    organization_slug = serializers.SlugField(max_length=255)
    project_slug = serializers.SlugField(max_length=255)
    sprint_id = serializers.IntegerField(min_value=1)


class AISprintSummaryResponseSerializer(serializers.Serializer):
    summary = serializers.CharField(max_length=2000)
    achievements = serializers.ListField(
        child=serializers.CharField(max_length=500), max_length=8
    )
    incomplete_work = serializers.ListField(
        child=serializers.CharField(max_length=500), max_length=8
    )
    scope_change_insights = serializers.ListField(
        child=serializers.CharField(max_length=500), max_length=5
    )
    risks = serializers.ListField(
        child=serializers.CharField(max_length=500), max_length=5
    )
    recommendations = serializers.ListField(
        child=serializers.CharField(max_length=500), max_length=5
    )
