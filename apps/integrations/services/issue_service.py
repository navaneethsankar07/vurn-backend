from django.db import transaction

from ..exceptions import GitRepositoryException
from ..models import GitIssue, GitRepository
from ..providers.base import GitIssueQuery
from ..providers.registry import GitProviderRegistry
from .repository_service import GitRepositoryService


class GitIssueService:

    @classmethod
    def get_repository_issues(
        cls,
        *,
        project,
        repository_id,
        state="open",
        sort="created",
        direction="desc",
        page=1,
        per_page=30
    ):
        integration = GitRepositoryService._get_github_integration(project=project)

        repository = GitRepository.objects.filter(
            id=repository_id, integration=integration
        ).first()

        if repository is None:
            raise GitRepositoryException("Connected repository not found.")

        provider_class = GitProviderRegistry.get(integration.provider)

        provider = provider_class(
            installation_id=(integration.installation.external_installation_id)
        )

        query = GitIssueQuery(
            state=state, sort=sort, direction=direction, page=page, per_page=per_page
        )

        github_response = provider.get_issues(repository, query)

        return repository, github_response

    @classmethod
    @transaction.atomic
    def sync_issues(cls, *, repository, github_issues):
        issues = []

        for github_issue in github_issues:

            issue, _ = GitIssue.objects.update_or_create(
                repository=repository,
                issue_number=github_issue["number"],
                defaults={
                    "external_id": str(github_issue["id"]),
                    "title": github_issue.get("title", ""),
                    "description": (github_issue.get("body") or ""),
                    "state": github_issue.get("state", "open"),
                    "author_username": (github_issue.get("user") or {}).get("login"),
                    "url": github_issue.get("html_url"),
                    "opened_at": github_issue.get("created_at"),
                    "closed_at": github_issue.get("closed_at"),
                },
            )

            issues.append(issue)

        return (
            GitIssue.objects.filter(id__in=[issue.id for issue in issues])
            .select_related(
                "work_item_link__issue__project", "work_item_link__issue__status"
            )
            .order_by("issue_number")
        )
