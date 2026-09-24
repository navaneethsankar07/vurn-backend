import logging

from django.db import IntegrityError, transaction
from django.db.models import Q, CharField
from django.db.models.functions import Cast

from apps.projects.exceptions import IssueAlreadyExistsException, IssueInvalidException
from apps.projects.models import Issue, Project
from apps.projects.models import Sprint, WorkflowStatus

logger = logging.getLogger(__name__)


class IssueService:

    @staticmethod
    def list_issues(
        *,
        project,
        search=None,
        issue_type=None,
        parent_id=None,
        epic_id=None,
        story_id=None,
        sprint_id=None,
        assignee_id=None,
        priority=None,
        status_id=None,
        sort="position",
    ):
        issues = Issue.objects.filter(project=project).select_related(
            "parent", "sprint", "status", "assignee", "reporter"
        )

        if search:
            search = search.strip()

            issues = issues.annotate(
                issue_key=Cast("issue_number", output_field=CharField())
            ).filter(Q(title__icontains=search) | Q(issue_number__icontains=search))

        if issue_type:
            issues = issues.filter(issue_type=issue_type)

        if parent_id:
            parent = Issue.objects.filter(id=parent_id, project=project).first()

            if parent is None:
                raise IssueInvalidException(
                    "The parent issue does not belong " "to this project."
                )

            issues = issues.filter(parent_id=parent_id)

        if epic_id:
            epic = Issue.objects.filter(
                id=epic_id, project=project, issue_type="epic"
            ).first()

            if epic is None:
                raise IssueInvalidException(
                    "The selected epic does not belong " "to this project."
                )

            epic_ids = IssueService._get_descendant_ids(
                project=project, parent_id=epic.id
            )

            epic_ids.append(epic.id)

            issues = issues.filter(id__in=epic_ids)

        if story_id:
            story = Issue.objects.filter(
                id=story_id, project=project, issue_type="story"
            ).first()

            if story is None:
                raise IssueInvalidException(
                    "The selected story does not belong " "to this project."
                )

            story_ids = IssueService._get_descendant_ids(
                project=project, parent_id=story.id
            )

            story_ids.append(story.id)

            issues = issues.filter(id__in=story_ids)

        if sprint_id:
            sprint_exists = Sprint.objects.filter(
                id=sprint_id, project=project
            ).exists()

            if not sprint_exists:
                raise IssueInvalidException(
                    "The sprint does not belong " "to this project."
                )

            issues = issues.filter(sprint_id=sprint_id)

        if assignee_id:
            assignee_exists = IssueService._is_project_member(
                project=project, user_id=assignee_id
            )

            if not assignee_exists:
                raise IssueInvalidException(
                    "The assignee is not a member " "of this project."
                )

            issues = issues.filter(assignee_id=assignee_id)

        if priority:
            issues = issues.filter(priority=priority)

        if status_id:
            status_exists = WorkflowStatus.objects.filter(
                id=status_id, project=project
            ).exists()

            if not status_exists:
                raise IssueInvalidException(
                    "The workflow status does not belong " "to this project."
                )

            issues = issues.filter(status_id=status_id)

        ordering = {
            "created_asc": "created_at",
            "created_desc": "-created_at",
            "updated_asc": "updated_at",
            "updated_desc": "-updated_at",
            "priority_asc": "priority",
            "priority_desc": "-priority",
            "position": "position",
        }

        issues = issues.order_by(ordering.get(sort, "position"), "id")

        return issues

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

    @staticmethod
    def _get_descendant_ids(*, project, parent_id):
        descendant_ids = []
        current_parent_ids = [parent_id]

        while current_parent_ids:
            children = list(
                Issue.objects.filter(
                    project=project, parent_id__in=current_parent_ids
                ).values_list("id", flat=True)
            )

            if not children:
                break

            descendant_ids.extend(children)
            current_parent_ids = children

        return descendant_ids

    @staticmethod
    def _is_project_member(*, project, user_id):
        if project.owner_id == user_id:
            return True

        return project.members.filter(user_id=user_id).exists()
