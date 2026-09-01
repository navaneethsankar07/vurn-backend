from ..constants import ORGANIZATION_PERMISSION_CODES
from ..exceptions import OrganizationNotFoundException
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
            }

        try:
            member = (
                OrganizationMember.objects.select_related("job_role")
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
