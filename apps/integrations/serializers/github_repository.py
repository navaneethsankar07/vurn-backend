from rest_framework import serializers

from ..models import GitCommit, GitIssue, GitIssueWorkItem, GitRepository


class GitHubRepositorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    full_name = serializers.CharField()
    private = serializers.BooleanField()
    html_url = serializers.URLField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    default_branch = serializers.CharField(allow_blank=True, allow_null=True)


class GitHubRepositoryOverviewSerializer(serializers.ModelSerializer):
    stars = serializers.IntegerField(
        source="github_repository.stargazers_count", read_only=True
    )
    forks = serializers.IntegerField(
        source="github_repository.forks_count", read_only=True
    )
    open_issues = serializers.IntegerField(
        source="github_repository.open_issues_count", read_only=True
    )
    language = serializers.CharField(
        source="github_repository.language", allow_null=True, read_only=True
    )
    github_created_at = serializers.DateTimeField(
        source="github_repository.created_at", read_only=True
    )
    github_updated_at = serializers.DateTimeField(
        source="github_repository.updated_at", read_only=True
    )

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
            "description",
            "is_archived",
            "stars",
            "forks",
            "open_issues",
            "language",
            "github_created_at",
            "github_updated_at",
        ]


class GitCommitQuerySerializer(serializers.Serializer):
    branch = serializers.CharField(required=False, allow_blank=False, max_length=255)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, default=5
    )


class GitCommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitCommit
        fields = [
            "id",
            "sha",
            "message",
            "author_name",
            "author_email",
            "author_username",
            "branch",
            "url",
            "committed_at",
            "created_at",
        ]


class GitHubBranchSerializer(serializers.Serializer):
    name = serializers.CharField()
    protected = serializers.BooleanField()
    is_default = serializers.BooleanField()


from rest_framework import serializers


class GitIssueQuerySerializer(serializers.Serializer):
    state = serializers.ChoiceField(
        choices=("open", "closed", "all"), required=False, default="open"
    )
    sort = serializers.ChoiceField(
        choices=("created", "updated", "comments"), required=False, default="created"
    )
    direction = serializers.ChoiceField(
        choices=("asc", "desc"), required=False, default="desc"
    )
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, default=5
    )


class GitIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitIssue
        fields = [
            "id",
            "external_id",
            "issue_number",
            "title",
            "description",
            "state",
            "author_username",
            "url",
            "opened_at",
            "closed_at",
            "created_at",
            "updated_at",
        ]


class GitIssueLinkSerializer(serializers.Serializer):
    issue_id = serializers.IntegerField(required=False, min_value=1)
    auto_match = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        issue_id = attrs.get("issue_id")
        auto_match = attrs.get("auto_match", False)

        if auto_match and issue_id is not None:
            raise serializers.ValidationError(
                "Provide issue_id or auto_match, not both."
            )

        if not auto_match and issue_id is None:
            raise serializers.ValidationError(
                "Provide an issue_id or enable auto_match."
            )

        return attrs


class GitIssueWorkItemSerializer(serializers.ModelSerializer):
    issue_key = serializers.CharField(source="issue.key", read_only=True)
    issue_title = serializers.CharField(source="issue.title", read_only=True)
    issue_type = serializers.CharField(source="issue.issue_type", read_only=True)

    class Meta:
        model = GitIssueWorkItem
        fields = [
            "id",
            "git_issue",
            "issue",
            "issue_key",
            "issue_title",
            "issue_type",
            "linked_at",
        ]
        read_only_fields = fields
