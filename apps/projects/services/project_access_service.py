from apps.organizations.services.organization_access_service import (
    OrganizationAccessService,
)
from ..exceptions import ProjectPermissionDeniedException


class ProjectAccessService:

    @staticmethod
    def can_edit_project(*, project, user) -> bool:
        if project.owner_id == user.id:
            return True

        if project.project_lead_id == user.id:
            return True

        return OrganizationAccessService.has_permission(
            organization=project.organization,
            user=user,
            permission_code="project.edit",
        )

    @staticmethod
    def can_archive_project(*, project, user) -> bool:
        organization = project.organization

        if organization.owner_id == user.id:
            return True

        if project.owner_id == user.id:
            return True

        if project.project_lead_id == user.id:
            return True

        access = OrganizationAccessService.get_user_access(
            organization=organization, user=user
        )

        return access["role"] == "admin"

    @staticmethod
    def can_delete_project(*, project, user) -> bool:
        organization = project.organization

        if organization.owner_id == user.id:
            return True

        if project.owner_id == user.id:
            return True

        access = OrganizationAccessService.get_user_access(
            organization=organization, user=user
        )

        return access["role"] == "admin"

    @staticmethod
    def validate_project_archive_access(*, project, user) -> None:
        if not ProjectAccessService.can_archive_project(project=project, user=user):
            raise ProjectPermissionDeniedException(
                "You do not have permission to archive this project."
            )

    @staticmethod
    def validate_project_delete_access(*, project, user) -> None:
        if not ProjectAccessService.can_delete_project(
            project=project,
            user=user,
        ):
            raise ProjectPermissionDeniedException(
                "You do not have permission to delete this project."
            )

    @staticmethod
    def validate_project_edit_access(*, project, user) -> None:

        if not ProjectAccessService.can_edit_project(
            project=project,
            user=user,
        ):
            raise ProjectPermissionDeniedException(
                "You do not have permission to edit this project."
            )
