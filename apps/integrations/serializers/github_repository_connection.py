from rest_framework import serializers

from ..models import GitRepository


class GitHubRepositoryConnectionSerializer(serializers.Serializer):
    repository_id = serializers.IntegerField(min_value=1)


from rest_framework import serializers


class GitHubConnectedRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GitRepository
        fields = [
            "id",
            "external_repository_id",
            "name",
            "full_name",
            "repository_url",
            "default_branch",
            "visibility",
            "is_archived",
        ]


class GitHubIntegrationStatusSerializer(serializers.Serializer):
    connected = serializers.BooleanField()
    provider = serializers.CharField()
    status = serializers.CharField(allow_null=True)
    account = serializers.DictField(allow_null=True)
    repositories = GitHubConnectedRepositorySerializer(many=True)


class GitHubInstallationCompleteSerializer(serializers.Serializer):
    installation_id = serializers.IntegerField(min_value=1)
    setup_action = serializers.CharField(max_length=20)
    state = serializers.CharField()
