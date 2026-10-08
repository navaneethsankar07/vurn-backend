from apps.projects.models import Project

from ..models import GitIntegration
from ..providers.registry import GitProviderRegistry


class GitRepositoryService:

    @staticmethod
    def get_available_repositories(*, project, user):
        integration = (
            GitIntegration.objects.select_related("installation")
            .filter(project=project, provider="github", status="active")
            .first()
        )

        if integration is None:
            raise ValueError("GitHub is not connected to this project.")

        installation = integration.installation

        provider_class = GitProviderRegistry.get(integration.provider)

        provider = provider_class(
            installation_id=(installation.external_installation_id)
        )

        return provider.get_repositories()
