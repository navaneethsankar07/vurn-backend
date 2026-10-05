from datetime import timedelta
import re

from django.db import IntegrityError, transaction
from django.db.models import Q


from ..exceptions import (
    SprintAlreadyExistsException,
    SprintCompletionBlockedException,
    SprintCompletionException,
    SprintInvalidException,
    SprintNotFoundException,
)
from apps.projects.models import Issue, Sprint

from .issue_sprint_history_service import IssueSprintHistoryService


class SprintService:

    @staticmethod
    def get_sprint(*, project, sprint_id):
        try:
            return Sprint.objects.get(id=sprint_id, project=project)
        except Sprint.DoesNotExist as exc:
            raise SprintNotFoundException("Sprint not found.") from exc

    @staticmethod
    def list_sprints(*, project, search=None, status=None, sort="created_desc"):
        queryset = Sprint.objects.filter(project=project).select_related("created_by")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(goal__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        sort_options = {
            "name_asc": "name",
            "name_desc": "-name",
            "start_date_asc": "start_date",
            "start_date_desc": "-start_date",
            "end_date_asc": "end_date",
            "end_date_desc": "-end_date",
            "created_asc": "created_at",
            "created_desc": "-created_at",
        }

        queryset = queryset.order_by(sort_options.get(sort, "-created_at"))

        return queryset

    @staticmethod
    @transaction.atomic
    def create_sprint(
        *,
        project,
        user,
        name,
        goal="",
        description="",
        start_date=None,
        end_date=None,
        estimated_days=None,
    ):
        if Sprint.objects.filter(project=project, name=name).exists():
            raise SprintAlreadyExistsException(
                "A sprint with this name already exists in this project."
            )

        if estimated_days is not None:
            end_date = start_date + timedelta(days=estimated_days - 1)

        if start_date > end_date:
            raise SprintInvalidException(
                "End date must be after or equal to the start date."
            )

        SprintService._validate_sprint_dates(
            project=project, start_date=start_date, end_date=end_date
        )

        try:
            return Sprint.objects.create(
                project=project,
                name=name,
                goal=goal,
                description=description,
                start_date=start_date,
                end_date=end_date,
                estimated_days=estimated_days,
                status="planned",
                created_by=user,
            )
        except IntegrityError as exc:
            raise SprintAlreadyExistsException("Unable to create the sprint.") from exc

    @staticmethod
    def _validate_sprint_dates(*, project, start_date, end_date, sprint_id=None):
        overlapping_sprints = Sprint.objects.filter(
            project=project, start_date__lte=end_date, end_date__gte=start_date
        )

        if sprint_id is not None:
            overlapping_sprints = overlapping_sprints.exclude(id=sprint_id)

        if overlapping_sprints.exists():
            raise SprintInvalidException(
                "Sprint dates overlap with an existing sprint."
            )

    @staticmethod
    @transaction.atomic
    def update_sprint(*, sprint, **validated_data):
        name = validated_data.get("name")

        if (
            name
            and Sprint.objects.filter(project=sprint.project, name=name)
            .exclude(id=sprint.id)
            .exists()
        ):
            raise SprintAlreadyExistsException(
                "A sprint with this name already exists " "in this project."
            )

        start_date = validated_data.get("start_date", sprint.start_date)

        end_date = validated_data.get("end_date", sprint.end_date)

        estimated_days = validated_data.get("estimated_days")

        if estimated_days is not None:
            end_date = start_date + timedelta(days=estimated_days - 1)

        if start_date > end_date:
            raise SprintInvalidException(
                "End date must be after or equal " "to the start date."
            )

        SprintService._validate_sprint_dates(
            project=sprint.project,
            start_date=start_date,
            end_date=end_date,
            sprint_id=sprint.id,
        )

        validated_data["start_date"] = start_date
        validated_data["end_date"] = end_date

        for field, value in validated_data.items():
            setattr(sprint, field, value)

        try:
            sprint.save()
        except IntegrityError as exc:
            raise SprintAlreadyExistsException("Unable to update the sprint.") from exc

        return sprint

    @staticmethod
    @transaction.atomic
    def start_sprint(*, sprint):
        if sprint.status != "planned":
            raise SprintInvalidException("Only planned sprints can be started.")

        active_sprint_exists = (
            Sprint.objects.filter(project=sprint.project, status="active")
            .exclude(id=sprint.id)
            .exists()
        )

        if active_sprint_exists:
            raise SprintInvalidException("This project already has an active sprint.")

        sprint.status = "active"
        sprint.save(update_fields=["status", "updated_at"])

        return sprint

    @staticmethod
    def get_sprint_completion_data(*, sprint):
        work_items = (
            Issue.objects.filter(
                project=sprint.project, sprint=sprint, deleted_at__isnull=True
            )
            .exclude(issue_type="subtask")
            .select_related("status", "parent")
        )

        incomplete_issues = list(work_items.exclude(status__category="done"))

        incomplete_subtasks = []

        if not incomplete_issues:
            incomplete_subtasks = list(
                Issue.objects.filter(
                    project=sprint.project,
                    sprint=sprint,
                    issue_type="subtask",
                    deleted_at__isnull=True,
                )
                .exclude(status__category="done")
                .select_related("status", "parent")
            )
        print(incomplete_subtasks)

        return {
            "can_complete": (not incomplete_issues and not incomplete_subtasks),
            "incomplete_issues": incomplete_issues,
            "incomplete_subtasks": incomplete_subtasks,
        }

    @staticmethod
    def _generate_next_sprint_name(*, project, current_name):
        match = re.match(r"^(.*?)(?:\s+(\d+))$", current_name.strip())

        if match:
            base_name = match.group(1).strip()
            number = int(match.group(2)) + 1
        else:
            base_name = current_name.strip()
            number = 1

        while True:
            name = f"{base_name} {number}"

            if not Sprint.objects.filter(project=project, name=name).exists():
                return name

            number += 1

    @staticmethod
    def _create_following_sprint(*, sprint, user):
        duration = (sprint.end_date - sprint.start_date).days + 1

        start_date = sprint.end_date + timedelta(days=1)

        end_date = start_date + timedelta(days=duration - 1)

        name = SprintService._generate_next_sprint_name(
            project=sprint.project, current_name=sprint.name
        )

        return Sprint.objects.create(
            project=sprint.project,
            name=name,
            goal="",
            description="",
            start_date=start_date,
            end_date=end_date,
            estimated_days=duration,
            status="planned",
            created_by=user,
        )

    @staticmethod
    def _get_completion_target_sprint(*, sprint, target_sprint_id):
        target_sprint = Sprint.objects.filter(
            id=target_sprint_id, project=sprint.project
        ).first()

        if target_sprint is None:
            raise SprintInvalidException("Target sprint not found.")

        if target_sprint.id == sprint.id:
            raise SprintInvalidException(
                "The current sprint cannot be used " "as the target sprint."
            )

        if target_sprint.status == "completed":
            raise SprintInvalidException(
                "Issues cannot be moved to a completed sprint."
            )

        return target_sprint

    @staticmethod
    @transaction.atomic
    def complete_sprint(
        *, project, sprint_id, user, incomplete_issue_action=None, target_sprint_id=None
    ):
        sprint = (
            Sprint.objects.select_for_update()
            .filter(id=sprint_id, project=project)
            .first()
        )

        if sprint is None:
            raise SprintNotFoundException("Sprint not found.")

        if sprint.status != "active":
            raise SprintCompletionException("Only an active sprint can be completed.")

        work_items = list(
            Issue.objects.select_for_update()
            .filter(project=project, sprint=sprint, deleted_at__isnull=True)
            .exclude(issue_type="subtask")
            .select_related("status")
        )

        incomplete_issues = [
            issue for issue in work_items if issue.status.category != "done"
        ]

        target_sprint = None

        if incomplete_issues:
            if incomplete_issue_action is None:
                raise SprintCompletionBlockedException(
                    "Incomplete issues require an action."
                )

            if incomplete_issue_action == "sprint":
                target_sprint = SprintService._get_completion_target_sprint(
                    sprint=sprint, target_sprint_id=target_sprint_id
                )

                target_sprint = Sprint.objects.select_for_update().get(
                    id=target_sprint.id
                )

            elif incomplete_issue_action == "new_sprint":
                target_sprint = SprintService._create_following_sprint(
                    sprint=sprint, user=user
                )

            elif incomplete_issue_action == "backlog":
                target_sprint = None

            else:
                raise SprintCompletionException("Invalid incomplete issue action.")

            incomplete_issue_ids = [issue.id for issue in incomplete_issues]

            if target_sprint is None:
                Issue.objects.filter(id__in=incomplete_issue_ids).update(sprint=None)

                Issue.objects.filter(
                    project=project,
                    parent_id__in=incomplete_issue_ids,
                    issue_type="subtask",
                    deleted_at__isnull=True,
                ).update(sprint=None)
            else:
                incomplete_issues_with_subtasks = list(
                    Issue.objects.filter(id__in=incomplete_issue_ids)
                )

                incomplete_subtasks = list(
                    Issue.objects.filter(
                        project=project,
                        parent_id__in=incomplete_issue_ids,
                        issue_type="subtask",
                        deleted_at__isnull=True,
                    )
                )

                Issue.objects.filter(id__in=incomplete_issue_ids).update(
                    sprint=target_sprint
                )

                Issue.objects.filter(
                    id__in=[subtask.id for subtask in incomplete_subtasks]
                ).update(sprint=target_sprint)

                IssueSprintHistoryService.create_history_bulk(
                    issues=incomplete_issues_with_subtasks, sprint=target_sprint
                )

                IssueSprintHistoryService.create_history_bulk(
                    issues=incomplete_subtasks, sprint=target_sprint
                )

        remaining_subtasks = (
            Issue.objects.select_for_update()
            .filter(
                project=project,
                sprint=sprint,
                issue_type="subtask",
                deleted_at__isnull=True,
            )
            .exclude(status__category="done")
            .select_related("status")
        )

        if remaining_subtasks.exists():
            raise SprintCompletionBlockedException(
                "Sprint cannot be completed because " "there are incomplete subtasks."
            )

        sprint.status = "completed"
        sprint.save(update_fields=["status", "updated_at"])

        return sprint, target_sprint

    @staticmethod
    def list_project_sprints_for_board(*, project):
        return Sprint.objects.filter(project=project).order_by("start_date", "id")
