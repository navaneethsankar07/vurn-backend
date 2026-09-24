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


class WorkflowStatusCannotBeDeletedException(WorkflowException):
    pass


class WorkflowTransitionNotFoundException(WorkflowException):
    pass


class WorkflowTransitionStatusException(WorkflowException):
    pass


class WorkflowTransitionAlreadyExistsException(WorkflowException):
    pass


class WorkflowTransitionInvalidException(WorkflowException):
    pass


class SprintException(ProjectException):
    pass


class SprintNotFoundException(SprintException):
    pass


class SprintAlreadyExistsException(SprintException):
    pass


class SprintInvalidException(SprintException):
    pass


class SprintInvalidException(SprintException):
    pass


class KanbanException(ProjectException):
    pass


class KanbanIssueNotFoundException(KanbanException):
    """Base exception for all kanban-related business exceptions."""


class KanbanStatusNotFoundException(KanbanException):
    pass


class KanbanInvalidMovementException(KanbanException):
    pass


class KanbanIssuePositionException(KanbanException):
    pass


class IssueException(ProjectException):
    """Base exception for all issues-related business exceptions."""


class IssueNotFoundException(IssueException):
    pass


class IssueAlreadyExistsException(IssueException):
    pass


class IssueInvalidException(IssueException):
    pass
