class ProjectException(Exception):
    """Base exception for all project-related business exceptions."""


class ProjectNotFoundException(ProjectException):
    pass


class ProjectAlreadyExistsException(ProjectException):
    pass


class ProjectCreationPermissionDeniedException(ProjectException):
    pass


class ProjectPermissionDeniedException(ProjectException):
    pass


class ProjectDeleteConfirmationException(ProjectException):
    pass


class ProjectMemberException(ProjectException):
    pass


class ProjectMemberAlreadyExistsException(ProjectMemberException):
    pass


class ProjectMemberUserNotFoundException(ProjectMemberException):
    pass


class ProjectMemberNotFoundException(ProjectMemberException):
    pass


class WorkflowException(ProjectException):
    pass


class WorkflowStatusAlreadyExistsException(WorkflowException):
    pass

class WorkflowStatusNotFoundException(WorkflowException):
    pass
