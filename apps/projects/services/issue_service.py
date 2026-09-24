import logging

from django.db import IntegrityError, transaction

from apps.projects.exceptions import IssueAlreadyExistsException, IssueInvalidException
from apps.projects.models import Issue, Project
from apps.projects.models import Sprint, WorkflowStatus

logger = logging.getLogger(__name__)


class IssueService:

    @staticmethod
    @transaction.atomic
    def create_issue(
        *,
        project,
        user,
        issue_type,
        title,
        description="",
        parent_id=None,
        sprint_id=None,
        status_id=None,
        assignee_id=None,
        priority="medium",
        story_points=None,
    ):
        parent = None

        if parent_id is not None:
            parent = Issue.objects.filter(id=parent_id, project=project).first()

            if parent is None:
                raise IssueInvalidException(
                    "The parent issue does not belong " "to this project."
                )

            IssueService._validate_parent(issue_type=issue_type, parent=parent)

        sprint = None

        if sprint_id is not None:
            sprint = Sprint.objects.filter(id=sprint_id, project=project).first()

            if sprint is None:
                raise IssueInvalidException(
                    "The sprint does not belong " "to this project."
                )

        if issue_type == "epic" and sprint is not None:
            raise IssueInvalidException("An epic cannot be assigned to a sprint.")

        status = None

        if status_id is not None:
            status = WorkflowStatus.objects.filter(
                id=status_id, project=project, is_archived=False
            ).first()

            if status is None:
                raise IssueInvalidException(
                    "The workflow status does not belong " "to this project."
                )
        else:
            status = WorkflowStatus.objects.filter(
                project=project, is_archived=False, is_default=True
            ).first()

            if status is None:
                raise IssueInvalidException(
                    "The project does not have a default " "workflow status."
                )

        assignee = None

        if assignee_id is not None:
            assignee = IssueService._get_project_member(
                project=project, user_id=assignee_id
            )

            if assignee is None:
                raise IssueInvalidException(
                    "The assignee is not a member " "of this project."
                )

        last_issue = (
            Issue.objects.select_for_update()
            .filter(project=project)
            .order_by("-issue_number")
            .first()
        )

        issue_number = last_issue.issue_number + 1 if last_issue else 1

        position = Issue.objects.filter(project=project, status=status).count()

        try:
            issue = Issue.objects.create(
                project=project,
                parent=parent,
                sprint=sprint,
                status=status,
                assignee=assignee,
                reporter=user,
                issue_number=issue_number,
                issue_type=issue_type,
                title=title,
                description=description,
                priority=priority,
                story_points=story_points,
                position=position,
            )
        except IntegrityError as exc:
            raise IssueAlreadyExistsException("Unable to create the issue.") from exc

        logger.info(
            "Issue created | issue=%s project=%s " "type=%s user=%s",
            issue.id,
            project.id,
            issue_type,
            user.id,
        )

        return issue

    @staticmethod
    def _validate_parent(*, issue_type, parent):
        allowed_parents = {
            "story": {"epic"},
            "task": {"epic", "story"},
            "bug": {"epic", "story"},
            "subtask": {"story", "task", "bug"},
        }

        if issue_type == "epic":
            if parent is not None:
                raise IssueInvalidException("An epic cannot have a parent.")
            return

        allowed = allowed_parents.get(issue_type, set())

        if parent.issue_type not in allowed:
            raise IssueInvalidException(
                f"A {issue_type} cannot have a " f"{parent.issue_type} as its parent."
            )

    @staticmethod
    def _get_project_member(*, project, user_id):
        if project.owner_id == user_id:
            return project.owner

        membership = (
            project.members.select_related("user").filter(user_id=user_id).first()
        )

        if membership is None:
            return None

        return membership.user
