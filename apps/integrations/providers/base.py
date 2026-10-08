from abc import ABC, abstractmethod


class GitProvider(ABC):

    @abstractmethod
    def get_repositories(self):
        pass

    @abstractmethod
    def get_repository(self, repository_id):
        pass

    @abstractmethod
    def get_commits(self, repository):
        pass

    @abstractmethod
    def get_pull_requests(self, repository):
        pass

    @abstractmethod
    def create_webhook(self, repository):
        pass

    @abstractmethod
    def delete_webhook(self, repository):
        pass
