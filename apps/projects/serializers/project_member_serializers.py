from rest_framework import serializers


class ProjectMemberCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    project_role = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )

    def validate_project_role(self, value):
        return value.strip()


class ProjectMemberSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    user_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    avatar = serializers.URLField(allow_null=True)
    project_role = serializers.CharField()
    joined_at = serializers.DateTimeField()
