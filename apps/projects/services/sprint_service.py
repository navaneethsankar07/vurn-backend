from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Q

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
        estimated_days=None
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
    def list_project_sprints_for_board(*, project):
        return Sprint.objects.filter(project=project).order_by("start_date", "id")
