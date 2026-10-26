from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        min_length=2,
        max_length=255,
        trim_whitespace=True,
    )


class SearchResultSerializer(serializers.Serializer):
    id = serializers.CharField()
    entity_type = serializers.ChoiceField(choices=("project", "issue", "sprint"))
    entity_id = serializers.CharField()
    organization_slug = serializers.CharField(
        allow_null=True,
        required=False,
    )
    project_id = serializers.CharField()
    project_slug = serializers.CharField(
        allow_null=True,
        required=False,
    )
    project_key = serializers.CharField(
        allow_null=True,
        required=False,
    )
    key = serializers.CharField(
        allow_null=True,
        required=False,
    )
    identifier = serializers.CharField(
        allow_null=True,
        required=False,
    )
    title = serializers.CharField()
    description = serializers.CharField(
        allow_blank=True,
        required=False,
    )
    status = serializers.CharField(
        allow_null=True,
        required=False,
    )
    priority = serializers.CharField(
        allow_null=True,
        required=False,
    )
    issue_type = serializers.CharField(
        allow_null=True,
        required=False,
    )
    updated_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
