from rest_framework import serializers


class GitHubRepositoryConnectionSerializer(serializers.Serializer):
    repository_id = serializers.IntegerField(min_value=1)
