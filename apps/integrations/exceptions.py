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


class GitRepositoryAlreadyConnectedException(GitRepositoryException):
    pass


class GitIssueLinkException(GitIntegrationException):
    pass


class GitIssueClosedException(GitIssueLinkException):
    pass


class GitIssueAlreadyLinkedException(GitIssueLinkException):
    pass


class GitIssueAutoMatchException(GitIssueLinkException):
    pass


class GitIssueLinkLimitException(GitIssueLinkException):
    pass
