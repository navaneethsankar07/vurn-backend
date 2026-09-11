from django.db import transaction

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
