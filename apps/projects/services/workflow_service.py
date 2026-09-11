from django.db import IntegrityError, transaction
from django.db.models import F
from ..exceptions import (
    WorkflowStatusAlreadyExistsException,
    WorkflowStatusNotFoundException,
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

    @staticmethod
    def _update_status_position(*, status, new_position):
        current_position = status.position

        status_count = WorkflowStatus.objects.filter(project=status.project).count()

        new_position = min(new_position, status_count - 1)

        if new_position == current_position:
            return

        if new_position < current_position:
            WorkflowStatus.objects.filter(
                project=status.project,
                position__gte=new_position,
                position__lt=current_position,
            ).exclude(id=status.id).update(position=F("position") + 1)
        else:
            WorkflowStatus.objects.filter(
                project=status.project,
                position__gt=current_position,
                position__lte=new_position,
            ).exclude(id=status.id).update(position=F("position") - 1)

        status.position = new_position

    @staticmethod
    @transaction.atomic
    def update_status(*, status, **validated_data):
        name = validated_data.get("name")

        if (
            name
            and WorkflowStatus.objects.filter(project=status.project, name=name)
            .exclude(id=status.id)
            .exists()
        ):
            raise WorkflowStatusAlreadyExistsException(
                "A status with this name already exists " "in this project."
            )

        if "position" in validated_data:
            position = validated_data.pop("position")

            WorkflowService._update_status_position(
                status=status, new_position=position
            )

        if validated_data.get("is_default") is True:
            WorkflowStatus.objects.filter(
                project=status.project, is_default=True
            ).exclude(id=status.id).update(is_default=False)

        for field, value in validated_data.items():
            setattr(status, field, value)

        try:
            status.save()
        except IntegrityError as exc:
            raise WorkflowStatusAlreadyExistsException(
                "Unable to update the workflow status."
            ) from exc

        return status

    @staticmethod
    def get_status(*, project, status_id):
        try:
            return WorkflowStatus.objects.get(id=status_id, project=project)
        except WorkflowStatus.DoesNotExist as exc:
            raise WorkflowStatusNotFoundException("Workflow status not found.") from exc
