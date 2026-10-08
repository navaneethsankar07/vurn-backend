from rest_framework import serializers


class GitHubRepositorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    full_name = serializers.CharField()
    private = serializers.BooleanField()
    html_url = serializers.URLField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    default_branch = serializers.CharField(allow_blank=True, allow_null=True)
