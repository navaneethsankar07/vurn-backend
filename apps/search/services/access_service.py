from django.db.models import Q

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService


class SearchAccessService:

    @staticmethod
    def get_allowed_project_ids(*, user):
        projects = (
            Project.objects.filter(
                deleted_at__isnull=True,
            )
            .filter(
                Q(organization__owner=user)
                | Q(organization__members__user=user)
                | Q(owner=user)
                | Q(project_lead=user)
            )
            .select_related(
                "organization",
                "organization__preferences",
            )
            .distinct()
        )

        allowed_ids = {
            "project": [],
            "issue": [],
            "sprint": [],
        }

        for project in projects.iterator():
            if not ProjectAccessService.can_view_project(
                project=project,
                user=user,
            ):
                continue

            allowed_ids["project"].append(project.id)

            if ProjectAccessService.can_view_issues(
                project=project,
                user=user,
            ):
                allowed_ids["issue"].append(project.id)

            if ProjectAccessService.can_view_sprints(
                project=project,
                user=user,
            ):
                allowed_ids["sprint"].append(project.id)

        return allowed_ids
