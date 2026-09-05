from apps.organizations.services.organization_access_service import (
    OrganizationAccessService,
)


class ProjectAccessService:

    @staticmethod
    def can_edit_project(
        *,
        project,
        user,
    ) -> bool:
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
    def validate_project_edit_access(
        *,
        project,
        user,
    ) -> None:
        from ..exceptions import ProjectPermissionDeniedException

        if not ProjectAccessService.can_edit_project(
            project=project,
            user=user,
        ):
            raise ProjectPermissionDeniedException(
                "You do not have permission to edit this project."
            )