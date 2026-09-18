from datetime import timedelta
import logging

from django.utils import timezone

from apps.projects.models import WorkflowStatus, WorkflowTransition
from apps.projects.exceptions import (
    KanbanInvalidMovementException,
    KanbanIssueNotFoundException,
)

logger = logging.getLogger(__name__)


class MockKanbanRepository:

    _issues = {}

    @classmethod
    def get_project_issues(cls, project_id):
        if project_id not in cls._issues:
            cls._issues[project_id] = cls._create_mock_issues()

        return cls._issues[project_id]

    @staticmethod
    def _create_mock_issues():
        now = timezone.now()

        return [
            {
                "id": 1,
                "key": "VURN-1",
                "title": "Design authentication flow",
                "issue_type": "story",
                "status_id": 1,
                "sprint_id": 1,
                "priority": "high",
                "assignee_id": 1,
                "position": 0,
                "created_at": now - timedelta(days=10),
                "updated_at": now - timedelta(days=2),
            },
            {
                "id": 2,
                "key": "VURN-2",
                "title": "Create authentication API",
                "issue_type": "task",
                "status_id": 2,
                "sprint_id": 1,
                "priority": "high",
                "assignee_id": 2,
                "position": 0,
                "created_at": now - timedelta(days=9),
                "updated_at": now - timedelta(days=1),
            },
            {
                "id": 3,
                "key": "VURN-3",
                "title": "Create login form",
                "issue_type": "task",
                "status_id": 2,
                "sprint_id": 1,
                "priority": "medium",
                "assignee_id": 1,
                "position": 1,
                "created_at": now - timedelta(days=8),
                "updated_at": now - timedelta(days=3),
            },
            {
                "id": 4,
                "key": "VURN-4",
                "title": "Fix expired token issue",
                "issue_type": "bug",
                "status_id": 3,
                "sprint_id": 1,
                "priority": "urgent",
                "assignee_id": 3,
                "position": 0,
                "created_at": now - timedelta(days=7),
                "updated_at": now,
            },
            {
                "id": 5,
                "key": "VURN-5",
                "title": "Add password reset tests",
                "issue_type": "task",
                "status_id": 3,
                "sprint_id": 2,
                "priority": "medium",
                "assignee_id": 2,
                "position": 1,
                "created_at": now - timedelta(days=6),
                "updated_at": now - timedelta(days=1),
            },
            {
                "id": 6,
                "key": "VURN-6",
                "title": "Update authentication UI",
                "issue_type": "story",
                "status_id": 4,
                "sprint_id": 1,
                "priority": "low",
                "assignee_id": 1,
                "position": 0,
                "created_at": now - timedelta(days=5),
                "updated_at": now - timedelta(days=2),
            },
        ]

    @classmethod
    def get_issue(cls, project_id, issue_id):
        issues = cls.get_project_issues(project_id)

        return next((issue for issue in issues if issue["id"] == issue_id), None)

    @classmethod
    def update_issue(cls, project_id, issue):
        issues = cls.get_project_issues(project_id)

        for index, current_issue in enumerate(issues):
            if current_issue["id"] == issue["id"]:
                issues[index] = issue
                return issue

        return None


class KanbanService:

    @staticmethod
    def get_board(*, project):
        logger.info("Fetching Kanban board | project=%s", project.id)

        statuses = WorkflowStatus.objects.filter(
            project=project, is_archived=False
        ).order_by("position", "id")

        logger.info("Kanban board fetched | project=%s", project.id)

        return statuses

    @staticmethod
    def list_column_issues(
        *,
        project,
        status_id,
        search=None,
        sprint_id=None,
        issue_type=None,
        assignee_id=None,
        priority=None,
        sort="position"
    ):
        logger.info(
            "Listing Kanban column issues | project=%s status=%s", project.id, status_id
        )

        status = WorkflowStatus.objects.filter(
            id=status_id, project=project, is_archived=False
        ).first()

        if status is None:
            logger.warning(
                "Kanban workflow status not found | " "project=%s status=%s",
                project.id,
                status_id,
            )

            raise KanbanInvalidMovementException("Workflow status not found.")

        issues = MockKanbanRepository.get_project_issues(project.id)

        issues = [issue for issue in issues if issue["status_id"] == status.id]

        if search:
            search = search.strip().lower()

            issues = [
                issue
                for issue in issues
                if search in issue["title"].lower() or search in issue["key"].lower()
            ]

        if sprint_id:
            issues = [issue for issue in issues if issue["sprint_id"] == sprint_id]

        if issue_type:
            issues = [issue for issue in issues if issue["issue_type"] == issue_type]

        if assignee_id:
            issues = [issue for issue in issues if issue["assignee_id"] == assignee_id]

        if priority:
            issues = [issue for issue in issues if issue["priority"] == priority]

        if sort == "priority_asc":
            priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

            issues.sort(key=lambda issue: priority_order[issue["priority"]])

        elif sort == "priority_desc":
            priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

            issues.sort(
                key=lambda issue: priority_order[issue["priority"]], reverse=True
            )

        elif sort == "created_asc":
            issues.sort(key=lambda issue: issue["created_at"])

        elif sort == "created_desc":
            issues.sort(key=lambda issue: issue["created_at"], reverse=True)

        elif sort == "updated_asc":
            issues.sort(key=lambda issue: issue["updated_at"])

        elif sort == "updated_desc":
            issues.sort(key=lambda issue: issue["updated_at"], reverse=True)

        else:
            issues.sort(key=lambda issue: issue["position"])

        logger.info(
            "Kanban column issues listed | project=%s " "status=%s count=%s",
            project.id,
            status.id,
            len(issues),
        )

        return status, issues

    @staticmethod
    def move_issue(*, project, issue_id, status_id):
        logger.info(
            "Moving Kanban issue | project=%s issue=%s " "target_status=%s",
            project.id,
            issue_id,
            status_id,
        )

        issue = MockKanbanRepository.get_issue(project.id, issue_id)

        if issue is None:
            logger.warning(
                "Kanban issue not found | project=%s issue=%s", project.id, issue_id
            )

            raise KanbanIssueNotFoundException("Issue not found.")

        target_status = WorkflowStatus.objects.filter(
            id=status_id, project=project, is_archived=False
        ).first()

        if target_status is None:
            logger.warning(
                "Kanban target workflow status not found | " "project=%s status=%s",
                project.id,
                status_id,
            )

            raise KanbanInvalidMovementException("Target workflow status not found.")

        if issue["status_id"] == target_status.id:
            return issue

        transition_exists = WorkflowTransition.objects.filter(
            project=project, from_status_id=issue["status_id"], to_status=target_status
        ).exists()

        if not transition_exists:
            logger.warning(
                "Kanban issue movement rejected | project=%s "
                "issue=%s target_status=%s",
                project.id,
                issue_id,
                target_status.id,
            )

            raise KanbanInvalidMovementException(
                "This issue cannot move to the selected status."
            )

        target_issues = [
            current_issue
            for current_issue in (MockKanbanRepository.get_project_issues(project.id))
            if current_issue["status_id"] == target_status.id
        ]

        issue["status_id"] = target_status.id
        issue["position"] = len(target_issues)
        issue["updated_at"] = timezone.now()

        MockKanbanRepository.update_issue(project.id, issue)

        logger.info(
            "Kanban issue moved | project=%s issue=%s " "target_status=%s position=%s",
            project.id,
            issue_id,
            target_status.id,
            issue["position"],
        )

        return issue

    @staticmethod
    def update_issue_position(*, project, issue_id, position):
        logger.info(
            "Updating Kanban issue position | project=%s " "issue=%s position=%s",
            project.id,
            issue_id,
            position,
        )

        issue = MockKanbanRepository.get_issue(project.id, issue_id)

        if issue is None:
            logger.warning(
                "Kanban issue not found for position update | " "project=%s issue=%s",
                project.id,
                issue_id,
            )

            raise KanbanIssueNotFoundException("Issue not found.")

        issues = MockKanbanRepository.get_project_issues(project.id)

        column_issues = [
            current_issue
            for current_issue in issues
            if current_issue["status_id"] == issue["status_id"]
            and current_issue["id"] != issue["id"]
        ]

        position = min(position, len(column_issues))

        column_issues.insert(position, issue)

        for index, current_issue in enumerate(column_issues):
            current_issue["position"] = index
            current_issue["updated_at"] = timezone.now()

        logger.info(
            "Kanban issue position updated | project=%s " "issue=%s position=%s",
            project.id,
            issue_id,
            position,
        )

        return issue
