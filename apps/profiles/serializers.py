from rest_framework import serializers

from apps.accounts.models import User


class ProfileUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "username",
            "email",
            "avatar",
            "created_at",
            "last_login",
        ]
        read_only_fields = fields


class ProfileStatisticsSerializer(serializers.Serializer):
    organizations_joined = serializers.IntegerField()
    projects = serializers.IntegerField()
    assigned_issues = serializers.IntegerField()
    completed_issues = serializers.IntegerField()
    comments = serializers.IntegerField()
    github_linked_projects = serializers.IntegerField()


class RecentActivitySerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()


class ProfileSerializer(serializers.Serializer):
    user = ProfileUserSerializer()
    statistics = ProfileStatisticsSerializer()
    recent_activity = RecentActivitySerializer(
        many=True,
    )
