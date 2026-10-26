from django.db import IntegrityError, transaction

from ..exceptions import GitRepositoryAlreadyConnectedException, GitRepositoryException

from ..models import GitIntegration, GitRepository
from ..providers.registry import GitProviderRegistry


class GitRepositoryService:

    @staticmethod
    def _get_github_integration(*, project):
        integration = (
            GitIntegration.objects.select_related("installation")
            .filter(project=project, provider="github", status="active")
            .first()
        )

        if integration is None:
            raise ValueError("GitHub is not connected to this project.")

        if not hasattr(integration, "installation"):
            raise ValueError("GitHub installation is not configured.")

        return integration

    @classmethod
    def get_available_repositories(cls, *, project):
        integration = cls._get_github_integration(project=project)

        provider_class = GitProviderRegistry.get(integration.provider)

        provider = provider_class(
            installation_id=(integration.installation.external_installation_id)
        )

        return provider.get_repositories()

    @classmethod
    @transaction.atomic
    def connect_repository(cls, *, project, repository_id):
        integration = cls._get_github_integration(project=project)

        provider_class = GitProviderRegistry.get(integration.provider)

        provider = provider_class(
            installation_id=(integration.installation.external_installation_id)
        )

        repository = provider.get_repository(repository_id)

        existing_repository = GitRepository.objects.filter(
            integration=integration, external_repository_id=str(repository["id"])
        ).first()

        if existing_repository is not None:
            raise GitRepositoryAlreadyConnectedException(
                "This repository is already connected."
            )

        try:
            git_repository = GitRepository.objects.create(
                integration=integration,
                external_repository_id=str(repository["id"]),
                owner=repository["owner"]["login"],
                name=repository["name"],
                full_name=repository["full_name"],
                repository_url=repository["html_url"],
                default_branch=repository.get("default_branch"),
                visibility=("private" if repository.get("private") else "public"),
                description=repository.get("description") or "",
                is_archived=repository.get("archived", False),
            )
        except IntegrityError as exc:
            raise GitRepositoryAlreadyConnectedException(
                "This repository is already connected."
            ) from exc

        return git_repository

    @staticmethod
    def get_github_integration_status(*, project):
        integration = (
            GitIntegration.objects.select_related("installation")
            .prefetch_related("repositories")
            .filter(project=project, provider="github")
            .first()
        )

        if integration is None:
            return {
                "connected": False,
                "provider": "github",
                "status": None,
                "account": None,
                "repositories": [],
            }

        installation = getattr(integration, "installation", None)

        account = None

        if installation is not None:
            account = {
                "login": installation.account_login,
                "type": installation.account_type,
            }

        return {
            "connected": True,
            "provider": integration.provider,
            "status": integration.status,
            "account": account,
            "repositories": integration.repositories.all(),
        }

    @classmethod
    def get_repository_overview(cls, *, project, repository_id):
        integration = cls._get_github_integration(project=project)

        repository = GitRepository.objects.filter(
            id=repository_id, integration=integration
        ).first()

        if repository is None:
            raise GitRepositoryException("Connected repository not found.")

        provider_class = GitProviderRegistry.get(integration.provider)

        provider = provider_class(
            installation_id=(integration.installation.external_installation_id)
        )

        github_repository = provider.get_repository_details(
            owner=repository.owner, repository=repository.name
        )

        repository.github_repository = github_repository

        return repository
