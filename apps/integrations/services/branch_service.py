from ..exceptions import GitRepositoryException
from ..models import GitRepository
from ..providers.registry import GitProviderRegistry
from .repository_service import GitRepositoryService


class GitBranchService:

    @classmethod
    def get_repository_branches(cls, *, project, repository_id):
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

        branches = provider.get_branches(repository)

        for branch in branches:
            branch["is_default"] = branch["name"] == repository.default_branch

        return repository, branches
