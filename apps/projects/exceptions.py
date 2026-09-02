class ProjectException(Exception):
    """Base exception for all project-related business exceptions."""


class ProjectAlreadyExistsException(
    ProjectException,
):
    pass


class ProjectCreationPermissionDeniedException(
    ProjectException,
):
    pass
