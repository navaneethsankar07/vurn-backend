from ..base import GitProvider
from ...exceptions import GitProviderException
from .authentication import GitHubAuthenticationService
from .client import GitHubClient


class GitHubProvider(GitProvider):

    def __init__(self, *, installation_id):
        self.installation_id = installation_id

    def _get_client(self):
        access_token = GitHubAuthenticationService.generate_installation_token(
            installation_id=self.installation_id
        )

        return GitHubClient(access_token=access_token)

    def get_repositories(self):
        client = self._get_client()

        data = client.get_installation_repositories()

        return data.get("repositories", [])

    def get_repository(self, repository_id):
        repositories = self.get_repositories()

        for repository in repositories:
            if str(repository["id"]) == str(repository_id):
                return repository

        raise GitProviderException("GitHub repository not found.")

    def get_repository_details(self, *, owner, repository):
        client = self._get_client()

        return client.get_repository(owner=owner, repository=repository)

    def get_commits(self, repository, query):
        client = self._get_client()

        return client.get_commits(
            owner=repository.owner,
            repository=repository.name,
            branch=query.branch,
            page=query.page,
            per_page=query.per_page,
        )

    def get_branches(self, repository):
        client = self._get_client()

        return client.get_branches(owner=repository.owner, repository=repository.name)

    def get_pull_requests(self, repository, query):
        client = self._get_client()

        return client.get_pull_requests(
            owner=repository.owner,
            repository=repository.name,
            state=query.state,
            page=query.page,
            per_page=query.per_page,
        )

    def create_webhook(self, repository):
        raise NotImplementedError

    def delete_webhook(self, repository):
        raise NotImplementedError
