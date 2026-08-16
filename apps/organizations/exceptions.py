class OrganizationException(Exception):
    """Base exception for organization business exceptions."""


class OrganizationNotFoundException(OrganizationException):
    pass
