class GitIntegrationException(Exception):
    pass


class GitProviderException(GitIntegrationException):
    pass


class GitProviderNotSupportedException(GitProviderException):
    pass


class GitAuthenticationException(GitProviderException):
    pass


class GitRepositoryException(GitProviderException):
    pass


class GitWebhookException(GitProviderException):
    pass
