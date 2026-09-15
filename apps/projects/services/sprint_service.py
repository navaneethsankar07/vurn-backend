from django.db import IntegrityError, transaction

from apps.projects.exceptions import (
    SprintAlreadyExistsException,
    SprintInvalidException,
    SprintNotFoundException,
)
from apps.projects.models import Sprint


class SprintService:

    @staticmethod
    def get_sprint(*, project, sprint_id):
        try:
            return Sprint.objects.get(id=sprint_id, project=project)
        except Sprint.DoesNotExist as exc:
            raise SprintNotFoundException("Sprint not found.") from exc

    @staticmethod
    def list_sprints(*, project):
        return (
            Sprint.objects.filter(project=project)
            .select_related("created_by")
            .order_by("-created_at")
        )

    @staticmethod
    @transaction.atomic
    def create_sprint(
        *, project, user, name, goal="", description="", start_date=None, end_date=None
    ):
        if Sprint.objects.filter(project=project, name=name).exists():
            raise SprintAlreadyExistsException(
                "A sprint with this name already exists in this project."
            )

        if start_date > end_date:
            raise SprintInvalidException(
                "End date must be after or equal to the start date."
            )

        try:
            return Sprint.objects.create(
                project=project,
                name=name,
                goal=goal,
                description=description,
                start_date=start_date,
                end_date=end_date,
                status="planned",
                created_by=user,
            )
        except IntegrityError as exc:
            raise SprintAlreadyExistsException("Unable to create the sprint.") from exc
