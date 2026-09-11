from django.db import IntegrityError, transaction
from django.db.models import F
from ..exceptions import (
    WorkflowStatusAlreadyExistsException,
)

from ..models import WorkflowStatus, WorkflowTransition


class WorkflowService:

    @staticmethod
    @transaction.atomic
    def create_default_workflow(*, project):
        statuses = WorkflowStatus.objects.bulk_create(
            [
                WorkflowStatus(
                    project=project,
                    name="Backlog",
                    category="backlog",
                    color="#6B7280",
                    icon="inbox",
                    position=0,
                    is_default=True,
                ),
                WorkflowStatus(
                    project=project,
                    name="Todo",
                    category="todo",
                    color="#3B82F6",
                    icon="circle",
                    position=1,
                ),
                WorkflowStatus(
                    project=project,
                    name="In Progress",
                    category="in_progress",
                    color="#F59E0B",
                    icon="loader",
                    position=2,
                ),
                WorkflowStatus(
                    project=project,
                    name="Done",
                    category="done",
                    color="#22C55E",
                    icon="check-circle",
                    position=3,
                ),
            ]
        )

        transitions = [
            WorkflowTransition(
                project=project,
                from_status=statuses[0],
                to_status=statuses[1],
                name="Start",
            ),
            WorkflowTransition(
                project=project,
                from_status=statuses[1],
                to_status=statuses[2],
                name="Start Progress",
            ),
            WorkflowTransition(
                project=project,
                from_status=statuses[2],
                to_status=statuses[3],
                name="Complete",
            ),
        ]

        WorkflowTransition.objects.bulk_create(transitions)

        return statuses

    @staticmethod
    def get_workflow(*, project):
        statuses = WorkflowStatus.objects.filter(
            project=project, is_archived=False
        ).order_by("position", "id")

        transitions = WorkflowTransition.objects.filter(project=project).order_by("id")

        return {"statuses": statuses, "transitions": transitions}

    @staticmethod
    @transaction.atomic
    def create_status(
        *,
        project,
        name,
        category,
        color,
        icon=None,
        position=0,
        is_default=False,
        allow_from_backlog=True,
        allow_incoming=True,
        allow_outgoing=True
    ):
        if WorkflowStatus.objects.filter(project=project, name=name).exists():
            raise WorkflowStatusAlreadyExistsException(
                "A status with this name already exists " "in this project."
            )

        status_count = WorkflowStatus.objects.filter(project=project).count()

        position = min(position, status_count)

        if is_default:
            WorkflowStatus.objects.filter(project=project, is_default=True).update(
                is_default=False
            )

        WorkflowStatus.objects.filter(project=project, position__gte=position).update(
            position=F("position") + 1
        )

        try:
            return WorkflowStatus.objects.create(
                project=project,
                name=name,
                category=category,
                color=color,
                icon=icon,
                position=position,
                is_default=is_default,
                allow_from_backlog=allow_from_backlog,
                allow_incoming=allow_incoming,
                allow_outgoing=allow_outgoing,
            )
        except IntegrityError as exc:
            raise WorkflowStatusAlreadyExistsException(
                "Unable to create the workflow status."
            ) from exc
