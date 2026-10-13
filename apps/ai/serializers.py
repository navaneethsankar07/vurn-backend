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
