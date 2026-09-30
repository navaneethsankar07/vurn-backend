from importlib.abc import PathEntryFinder
import logging

from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

from ..models import Issue, WorkflowStatus, WorkflowTransition
from ..exceptions import (
    KanbanInvalidMovementException,
    KanbanIssueNotFoundException,
    KanbanIssuePositionException,
    KanbanStatusNotFoundException,
)

logger = logging.getLogger(__name__)


class KanbanService:

    @staticmethod
    def get_board(*, project):
        return WorkflowStatus.objects.filter(
            project=project, is_archived=False
        ).order_by("position", "id")

    @staticmethod
    def list_column_issues(
        *,
        project,
        status_id,
        search=None,
        sprint_id=None,
        parent_id=None,
        issue_type=None,
        assignee_id=None,
        priority=None,
        sort="position"
    ):
        status = WorkflowStatus.objects.filter(
            id=status_id, project=project, is_archived=False
        ).first()

        if status is None:
            raise KanbanStatusNotFoundException("Workflow status not found.")

        issues = (
            Issue.objects.filter(
                project=project, status=status, deleted_at__isnull=True
            )
            .exclude(issue_type__in=["subtask", "epic"])
            .select_related("parent", "sprint", "status", "assignee", "reporter")
        )

        if search:
            search = search.strip()

            issues = issues.filter(
                Q(title__icontains=search) | Q(issue_number__icontains=search)
            )

        if sprint_id:
            issues = issues.filter(sprint_id=sprint_id)

        if parent_id:
            issues = issues.filter(parent_id=parent_id)

        if issue_type:
            issues = issues.filter(issue_type=issue_type)

        if assignee_id:
            issues = issues.filter(assignee_id=assignee_id)

        if priority:
            issues = issues.filter(priority=priority)

        ordering = {
            "created_asc": "created_at",
            "created_desc": "-created_at",
            "updated_asc": "updated_at",
            "updated_desc": "-updated_at",
            "position": "position",
        }

        if sort == "priority_asc":
            priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

            issues = sorted(issues, key=lambda issue: priority_order[issue.priority])
        elif sort == "priority_desc":
            priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

            issues = sorted(
                issues, key=lambda issue: priority_order[issue.priority], reverse=True
            )
        else:
            issues = issues.order_by(ordering.get(sort, "position"), "id")

        return status, issues

    @staticmethod
    @transaction.atomic
    def move_issue(*, project, issue_id, status_id):
        issue = (
            Issue.objects.filter(project=project, id=issue_id)
            .select_for_update()
            .first()
        )

        if issue is None:
            raise KanbanIssueNotFoundException("Issue not found.")

        target_status = WorkflowStatus.objects.filter(
            id=status_id, project=project, is_archived=False
        ).first()

        if target_status is None:
            raise KanbanInvalidMovementException("Target workflow status not found.")

        if issue.status_id == target_status.id:
            return issue

        transition_exists = WorkflowTransition.objects.filter(
            project=project,
            from_status_id=issue.status_id,
            to_status_id=target_status.id,
        ).exists()

        if not transition_exists:
            raise KanbanInvalidMovementException(
                "This status transition is not configured for the project."
            )

        old_status_id = issue.status_id

        target_position = (
            Issue.objects.filter(project=project, status=target_status)
            .exclude(issue_type="subtask")
            .count()
        )

        Issue.objects.filter(
            project=project, status_id=old_status_id, position__gt=issue.position
        ).update(position=models.F("position") - 1)

        issue.status = target_status
        issue.position = target_position
        issue.updated_at = timezone.now()

        issue.save(update_fields=["status", "position", "updated_at"])

        return issue

    @staticmethod
    @transaction.atomic
    def update_issue_position(*, project, issue_id, position):
        issue = (
            Issue.objects.filter(project=project, id=issue_id)
            .select_for_update()
            .first()
        )

        if issue is None:
            raise KanbanIssueNotFoundException("Issue not found.")

        column_issues = list(
            Issue.objects.filter(project=project, status_id=issue.status_id)
            .exclude(issue_type="subtask")
            .exclude(id=issue.id)
            .select_for_update()
            .order_by("position", "id")
        )

        if position > len(column_issues):
            position = len(column_issues)

        if position < 0:
            raise KanbanIssuePositionException("Issue position cannot be negative.")

        column_issues.insert(position, issue)

        for index, current_issue in enumerate(column_issues):
            current_issue.position = index

            current_issue.save(update_fields=["position", "updated_at"])

        return issue
