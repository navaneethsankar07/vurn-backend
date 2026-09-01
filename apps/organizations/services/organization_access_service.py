from ..constants import ORGANIZATION_PERMISSION_CODES
from ..exceptions import (
    OrganizationInvitationPermissionDeniedException,
    OrganizationNotFoundException,
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
            return {
                "role": "owner",
                "job_role": None,
                "permissions": ["*"],
                "has_full_access": True,
                "can_invite_members": True,
            }

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
            return {
                "role": "admin",
                "job_role": job_role,
                "permissions": ["*"],
                "has_full_access": True,
                "can_invite_members": (
                    organization.preferences.allow_admin_invitations
                ),
            }

        permissions = []

        if member.job_role:
            permissions = [
                role_permission.permission.code
                for role_permission in member.job_role.role_permissions.all()
            ]

        return {
            "role": "member",
            "job_role": job_role,
            "permissions": permissions,
            "has_full_access": False,
            "can_invite_members": (organization.preferences.allow_member_invitations),
        }

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
