from django.db import transaction

from ..exceptions import GitRepositoryException
from ..models import GitPullRequest, GitRepository
from ..providers.base import GitPullRequestQuery
from ..providers.registry import GitProviderRegistry
from .repository_service import GitRepositoryService


class GitPullRequestService:

    @classmethod
    def get_repository_pull_requests(
        cls, *, project, repository_id, state="open", page=1, per_page=30
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

        query = GitPullRequestQuery(state=state, page=page, per_page=per_page)

        github_response = provider.get_pull_requests(repository, query)

        return repository, github_response

    @classmethod
    @transaction.atomic
    def sync_pull_requests(cls, *, repository, github_pull_requests):
        pull_requests = []

        for github_pr in github_pull_requests:
            pull_request, _ = GitPullRequest.objects.update_or_create(
                repository=repository,
                pr_number=github_pr["number"],
                defaults={
                    "external_id": str(github_pr["id"]),
                    "title": github_pr.get("title", ""),
                    "description": (github_pr.get("body") or ""),
                    "state": cls._get_pr_state(github_pr),
                    "draft": github_pr.get("draft", False),
                    "author_username": (github_pr.get("user") or {}).get("login"),
                    "source_branch": (github_pr.get("head") or {}).get("ref"),
                    "target_branch": (github_pr.get("base") or {}).get("ref"),
                    "url": github_pr.get("html_url"),
                    "opened_at": github_pr.get("created_at"),
                    "merged_at": github_pr.get("merged_at"),
                    "closed_at": github_pr.get("closed_at"),
                },
            )

            pull_requests.append(pull_request)

        return pull_requests

    @staticmethod
    def _get_pr_state(pull_request):
        if pull_request.get("merged_at"):
            return "merged"

        return pull_request.get("state", "open")
