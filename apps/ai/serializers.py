from rest_framework import serializers


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
