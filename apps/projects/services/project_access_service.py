from apps.organizations.services.organization_access_service import (
    OrganizationAccessService,
)
from ..exceptions import ProjectPermissionDeniedException


class ProjectAccessService:

    @staticmethod
    def can_view_project(*, project, user) -> bool:
        organization = project.organization

        if organization.owner_id == user.id:
            return True

        if project.owner_id == user.id:
            return True

        if project.project_lead_id == user.id:
            return True

        return OrganizationAccessService.has_permission(
            organization=organization, user=user, permission_code="project.view"
        )

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
    def can_add_project_members(*, project, user) -> bool:
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
    def can_remove_project_member(*, project, user) -> bool:
        organization = project.organization

        if organization.owner_id == user.id:
            return True

        if project.owner_id == user.id:
            return True

        return False

    @staticmethod
    def can_manage_workflow(*, project, user):
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
    def validate_project_view_access(*, project, user) -> None:
        if not ProjectAccessService.can_view_project(project=project, user=user):
            raise ProjectPermissionDeniedException(
                "You do not have permission to view this project."
            )

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

    @staticmethod
    def validate_add_project_member_access(*, project, user) -> None:
        if not ProjectAccessService.can_add_project_members(project=project, user=user):
            raise ProjectPermissionDeniedException(
                "You do not have permission to add members to this project."
            )

    @staticmethod
    def validate_remove_project_member_access(*, project, user) -> None:
        if not ProjectAccessService.can_remove_project_member(
            project=project, user=user
        ):
            raise ProjectPermissionDeniedException(
                "You do not have permission to remove " "members from this project."
            )

    @staticmethod
    def validate_workflow_management_access(*, project, user):
        if not ProjectAccessService.can_manage_workflow(project=project, user=user):
            raise ProjectPermissionDeniedException(
                "You do not have permission to manage " "the project workflow."
            )
