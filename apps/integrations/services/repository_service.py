from ..models import GitIntegration
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
    def get_repository(cls, *, project, repository_id):
        integration = cls._get_github_integration(project=project)

        provider_class = GitProviderRegistry.get(integration.provider)

        provider = provider_class(
            installation_id=(integration.installation.external_installation_id)
        )

        return provider.get_repository(repository_id)
