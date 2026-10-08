from rest_framework import serializers

from ..models import GitPullRequest


class GitPullRequestQuerySerializer(serializers.Serializer):
    state = serializers.ChoiceField(
        choices=("open", "closed", "all"), required=False, default="open"
    )
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, default=5
    )


class GitPullRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitPullRequest
        fields = [
            "id",
            "external_id",
            "pr_number",
            "title",
            "description",
            "state",
            "draft",
            "author_username",
            "source_branch",
            "target_branch",
            "url",
            "opened_at",
            "merged_at",
            "closed_at",
            "created_at",
        ]
