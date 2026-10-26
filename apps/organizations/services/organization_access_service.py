from ..constants import ORGANIZATION_PERMISSION_CODES
from ..exceptions import (
    OrganizationInvitationPermissionDeniedException,
    OrganizationNotFoundException,
    OrganizationPermissionDeniedException,
    OrganizationProjectCreationPermissionDeniedException,
)
from ..models import OrganizationMember


class OrganizationAccessService:

    @staticmethod
    def get_user_access(
        *,
        organization,
        user,
    ):
        if organization.owner_id == user.id:
            access = {
                "role": "owner",
                "job_role": None,
                "permissions": ["*"],
                "has_full_access": True,
            }

        else:
            try:
                member = (
                    OrganizationMember.objects.select_related(
                        "job_role",
                    )
                    .prefetch_related(
                        "job_role__role_permissions__permission",
                    )
                    .get(
                        organization=organization,
                        user=user,
                    )
                )

            except OrganizationMember.DoesNotExist:
                raise OrganizationNotFoundException("Organization not found.")

            job_role = None

            if member.job_role:
                job_role = {
                    "id": member.job_role.id,
                    "name": member.job_role.name,
                }

            if member.role == "admin":
                access = {
                    "role": "admin",
                    "job_role": job_role,
                    "permissions": ["*"],
                    "has_full_access": True,
                }

            else:
                permissions = []

                if member.job_role:
                    permissions = [
                        role_permission.permission.code
                        for role_permission in member.job_role.role_permissions.all()
                    ]

                access = {
                    "role": "member",
                    "job_role": job_role,
                    "permissions": permissions,
                    "has_full_access": False,
                }

        access["can_invite_members"] = OrganizationAccessService._can_invite_members(
            organization=organization,
            access=access,
        )

        access["can_create_projects"] = OrganizationAccessService._can_create_projects(
            organization=organization,
            access=access,
        )

        return access

    @staticmethod
    def _can_invite_members(
        *,
        organization,
        access,
    ) -> bool:
        if access["role"] == "owner":
            return True

        if access["role"] == "admin":
            return organization.preferences.allow_admin_invitations

        if organization.preferences.allow_member_invitations:
            return True

        return "member.invite" in access["permissions"]

    @staticmethod
    def _can_create_projects(
        *,
        organization,
        access,
    ) -> bool:
        if access["role"] in ("owner", "admin"):
            return True

        if not organization.preferences.allow_member_project_creation:
            return False

        return "project.create" in access["permissions"]

    @staticmethod
    def has_permission(
        *,
        organization,
        user,
        permission_code,
    ) -> bool:
        if permission_code not in ORGANIZATION_PERMISSION_CODES:
            return False

        access = OrganizationAccessService.get_user_access(
            organization=organization,
            user=user,
        )

        return access["has_full_access"] or permission_code in access["permissions"]

    @staticmethod
    def can_invite_members(
        *,
        organization,
        user,
    ) -> bool:
        access = OrganizationAccessService.get_user_access(
            organization=organization,
            user=user,
        )

        return access["can_invite_members"]

    @staticmethod
    def can_create_projects(
        *,
        organization,
        user,
    ) -> bool:
        access = OrganizationAccessService.get_user_access(
            organization=organization,
            user=user,
        )

        return access["can_create_projects"]

    @staticmethod
    def validate_member_invitation_access(
        *,
        organization,
        user,
    ) -> None:
        if not OrganizationAccessService.can_invite_members(
            organization=organization,
            user=user,
        ):
            raise OrganizationInvitationPermissionDeniedException(
                "You do not have permission to invite members."
            )

    @staticmethod
    def validate_permission(
        *,
        organization,
        user,
        permission_code,
    ) -> None:
        if not OrganizationAccessService.has_permission(
            organization=organization,
            user=user,
            permission_code=permission_code,
        ):
            raise OrganizationPermissionDeniedException(
                "You do not have permission to perform this action."
            )

    @staticmethod
    def validate_project_creation_access(
        *,
        organization,
        user,
    ) -> None:
        if not OrganizationAccessService.can_create_projects(
            organization=organization,
            user=user,
        ):
            raise OrganizationProjectCreationPermissionDeniedException(
                "You do not have permission to create projects."
            )
