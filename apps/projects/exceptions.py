class ProjectException(Exception):
    """Base exception for all project-related business exceptions."""


class ProjectNotFoundException(
    ProjectException,
):
    pass


class ProjectAlreadyExistsException(
    ProjectException,
):
    pass


class ProjectCreationPermissionDeniedException(
    ProjectException,
):
    pass


class ProjectPermissionDeniedException(
    ProjectException,
):
    pass
