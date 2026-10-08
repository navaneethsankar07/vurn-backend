from django.conf import settings
from django.db import models

from .constants import (
    GIT_INTEGRATION_STATUS_CHOICES,
    GIT_PROVIDER_CHOICES,
    GIT_PULL_REQUEST_STATE_CHOICES,
    GIT_REPOSITORY_VISIBILITY_CHOICES,
    GIT_WEBHOOK_STATUS_CHOICES,
)


class GitIntegration(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="git_integrations"
    )
    provider = models.CharField(max_length=20, choices=GIT_PROVIDER_CHOICES)
    status = models.CharField(
        max_length=20, choices=GIT_INTEGRATION_STATUS_CHOICES, default="active"
    )
    connected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="connected_git_integrations",
    )
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "git_integrations"
        constraints = [
            models.UniqueConstraint(
                fields=("project", "provider"),
                name="uq_git_integration_project_provider",
            )
        ]
        indexes = [
            models.Index(fields=("project",), name="idx_git_integrations_project"),
            models.Index(fields=("provider",), name="idx_git_integrations_provider"),
            models.Index(fields=("status",), name="idx_git_integrations_status"),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.provider}"


class GitProviderInstallation(models.Model):
    integration = models.OneToOneField(
        GitIntegration, on_delete=models.CASCADE, related_name="installation"
    )
    provider = models.CharField(max_length=20, choices=GIT_PROVIDER_CHOICES)
    external_installation_id = models.CharField(max_length=100)
    account_login = models.CharField(max_length=255)
    account_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "git_provider_installations"
        indexes = [
            models.Index(fields=("provider",), name="idx_git_installations_provider"),
            models.Index(
                fields=("account_login",), name="idx_git_installations_account"
            ),
        ]

    def __str__(self):
        return f"{self.provider} - {self.account_login}"


class GitRepository(models.Model):
    integration = models.ForeignKey(
        GitIntegration, on_delete=models.CASCADE, related_name="repositories"
    )
    external_repository_id = models.CharField(max_length=100)
    owner = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=511)
    repository_url = models.URLField(max_length=1000)
    default_branch = models.CharField(max_length=255, blank=True, null=True)
    visibility = models.CharField(
        max_length=20, choices=GIT_REPOSITORY_VISIBILITY_CHOICES, blank=True, null=True
    )
    description = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "git_repositories"
        constraints = [
            models.UniqueConstraint(
                fields=("integration", "external_repository_id"),
                name="uq_git_repository_external",
            )
        ]
        indexes = [
            models.Index(fields=("integration",), name="idx_git_repo_integration"),
            models.Index(fields=("full_name",), name="idx_git_repositories_full_name"),
        ]

    def __str__(self):
        return self.full_name


class GitCommit(models.Model):
    repository = models.ForeignKey(
        GitRepository, on_delete=models.CASCADE, related_name="commits"
    )
    sha = models.CharField(max_length=64)
    message = models.TextField()
    author_name = models.CharField(max_length=255, blank=True, null=True)
    author_email = models.EmailField(max_length=254, blank=True, null=True)
    author_username = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=1000, blank=True, null=True)
    committed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "git_commits"
        constraints = [
            models.UniqueConstraint(
                fields=("repository", "sha"), name="uq_git_commit_sha"
            )
        ]
        indexes = [
            models.Index(fields=("repository",), name="idx_git_commits_repository"),
            models.Index(fields=("committed_at",), name="idx_git_commits_committed_at"),
        ]

    def __str__(self):
        return self.sha


class GitPullRequest(models.Model):
    repository = models.ForeignKey(
        GitRepository, on_delete=models.CASCADE, related_name="pull_requests"
    )
    external_id = models.CharField(max_length=100)
    pr_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    state = models.CharField(max_length=20, choices=GIT_PULL_REQUEST_STATE_CHOICES)
    author_username = models.CharField(max_length=255, blank=True, null=True)
    source_branch = models.CharField(max_length=255, blank=True, null=True)
    target_branch = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=1000)
    draft = models.BooleanField(default=False)
    opened_at = models.DateTimeField()
    merged_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "git_pull_requests"
        constraints = [
            models.UniqueConstraint(
                fields=("repository", "pr_number"), name="uq_git_pr_number"
            ),
            models.UniqueConstraint(
                fields=("repository", "external_id"), name="uq_git_pr_external"
            ),
        ]
        indexes = [
            models.Index(fields=("repository",), name="idx_git_pr_repository"),
            models.Index(fields=("state",), name="idx_git_pr_state"),
        ]

    def __str__(self):
        return f"{self.repository.full_name}#{self.pr_number}"


class GitCommitIssue(models.Model):
    commit = models.ForeignKey(
        GitCommit, on_delete=models.CASCADE, related_name="issue_links"
    )
    issue = models.ForeignKey(
        "projects.Issue", on_delete=models.CASCADE, related_name="git_commit_links"
    )
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "git_commit_issues"
        constraints = [
            models.UniqueConstraint(
                fields=("commit", "issue"), name="uq_git_commit_issue"
            )
        ]
        indexes = [
            models.Index(fields=("commit",), name="idx_git_commit_issues_commit"),
            models.Index(fields=("issue",), name="idx_git_commit_issues_issue"),
        ]


class GitPullRequestIssue(models.Model):
    pull_request = models.ForeignKey(
        GitPullRequest, on_delete=models.CASCADE, related_name="issue_links"
    )
    issue = models.ForeignKey(
        "projects.Issue",
        on_delete=models.CASCADE,
        related_name="git_pull_request_links",
    )
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "git_pull_request_issues"
        constraints = [
            models.UniqueConstraint(
                fields=("pull_request", "issue"), name="uq_git_pr_issue"
            )
        ]
        indexes = [
            models.Index(fields=("pull_request",), name="idx_git_pr_issues_pr"),
            models.Index(fields=("issue",), name="idx_git_pr_issues_issue"),
        ]


class GitWebhookDelivery(models.Model):
    integration = models.ForeignKey(
        GitIntegration, on_delete=models.CASCADE, related_name="webhook_deliveries"
    )
    provider = models.CharField(max_length=20)
    delivery_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20, choices=GIT_WEBHOOK_STATUS_CHOICES, default="received"
    )
    payload = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "git_webhook_deliveries"
        constraints = [
            models.UniqueConstraint(
                fields=("provider", "delivery_id"), name="uq_git_webhook_delivery"
            )
        ]
        indexes = [
            models.Index(fields=("integration",), name="idx_git_webhooks_integration"),
            models.Index(fields=("event_type",), name="idx_git_webhooks_event"),
            models.Index(fields=("status",), name="idx_git_webhooks_status"),
            models.Index(fields=("received_at",), name="idx_git_webhooks_received"),
        ]

    def __str__(self):
        return self.delivery_id
