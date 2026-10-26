from django.db import transaction


from ..providers.base import GitCommitQuery
from ..exceptions import GitRepositoryException
from ..models import GitCommit, GitRepository
from ..providers.registry import GitProviderRegistry
from .repository_service import GitRepositoryService


class GitCommitService:

    @classmethod
    def get_repository_commits(
        cls, *, project, repository_id, branch=None, page=1, per_page=30
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

        query = GitCommitQuery(
            branch=branch or repository.default_branch, page=page, per_page=per_page
        )

        github_response = provider.get_commits(repository, query)

        return (repository, github_response, query.branch)

    @classmethod
    @transaction.atomic
    def sync_commits(cls, *, repository, github_commits, branch):
        commits = []

        for github_commit in github_commits:
            commit_data = github_commit.get("commit") or {}
            author = commit_data.get("author") or {}

            commit, _ = GitCommit.objects.update_or_create(
                repository=repository,
                sha=github_commit["sha"],
                defaults={
                    "message": commit_data.get("message", ""),
                    "author_name": author.get("name"),
                    "author_email": author.get("email"),
                    "author_username": (github_commit.get("author") or {}).get("login"),
                    "branch": branch,
                    "url": github_commit.get("html_url"),
                    "committed_at": (commit_data.get("committer", {}).get("date")),
                },
            )

            commits.append(commit)

        return commits
