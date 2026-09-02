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


class OrganizationPermissionDeniedException(
    OrganizationException,
):
    pass


class OrganizationProjectCreationPermissionDeniedException(
    OrganizationException,
):
    pass


class OrganizationRoleException(OrganizationException):
    """Base exception for organization role business exceptions."""


class InvalidOrganizationRolePermissionsException(
    OrganizationRoleException,
):
    pass


class OrganizationInvitationException(OrganizationException):
    """Base exception for organization invitation business exceptions."""


class OrganizationInvitationExpiredException(
    OrganizationInvitationException,
):
    pass


class OrganizationInvitationNotFoundException(
    OrganizationInvitationException,
):
    pass


class OrganizationInvitationEmailMismatchException(
    OrganizationInvitationException,
):
    pass


class OrganizationInvitationPermissionDeniedException(
    OrganizationInvitationException,
):
    pass


class OrganizationMemberAlreadyExistsException(
    OrganizationInvitationException,
):
    pass


class OrganizationInvitationAlreadyExistsException(
    OrganizationInvitationException,
):
    pass


class OrganizationInvitationRecipientAlreadyMemberException(
    OrganizationInvitationException,
):
    pass


class OrganizationInvitationRecipientIsOwnerException(
    OrganizationInvitationException,
):
    pass
