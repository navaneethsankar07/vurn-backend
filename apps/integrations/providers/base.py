from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GitCommitQuery:
    branch: str | None = None
    page: int = 1
    per_page: int = 30


@dataclass
class GitPullRequestQuery:
    state: str = "open"
    page: int = 1
    per_page: int = 30


class GitProvider(ABC):

    @abstractmethod
    def get_repositories(self):
        pass

    @abstractmethod
    def get_repository(self, repository_id):
        pass

    @abstractmethod
    def get_commits(self, repository, query):
        pass

    @abstractmethod
    def get_branches(self, repository):
        pass

    @abstractmethod
    def get_pull_requests(self, repository, query):
        pass

    @abstractmethod
    def create_webhook(self, repository):
        pass

    @abstractmethod
    def delete_webhook(self, repository):
        pass
