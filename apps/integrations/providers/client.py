import requests

from ..exceptions import GitProviderException


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self, *, access_token):
        self.access_token = access_token

    def _request(self, *, method, endpoint, params=None):
        response = requests.request(
            method,
            f"{self.BASE_URL}{endpoint}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.access_token}",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            params=params,
            timeout=15,
        )

        if not response.ok:
            raise GitProviderException("GitHub API request failed.")

        return response.json()

    def get_installation_repositories(self):
        return self._request(method="GET", endpoint="/installation/repositories")

    def get_repository(self, *, owner, repository):
        return self._request(method="GET", endpoint=f"/repos/{owner}/{repository}")
