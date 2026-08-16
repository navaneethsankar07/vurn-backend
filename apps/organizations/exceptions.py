class OrganizationException(Exception):
    """Base exception for organization business exceptions."""


class OrganizationNotFoundException(OrganizationException):
    pass


class OrganizationNameMismatchException(
    OrganizationException,
):
    pass


class InvalidOrganizationDeleteOTPException(
    OrganizationException,
):
    pass


class OrganizationDeleteRequestExpiredException(
    OrganizationException,
):
    pass


class OrganizationAlreadyArchivedException(
    OrganizationException,
):
    pass


class OrganizationAlreadyDeletedException(
    OrganizationException,
):
    pass
