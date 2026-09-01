from django.db.models import Q

from ..models import OrganizationMember


class OrganizationMemberService:

    @staticmethod
    def list_members(
        *,
        organization,
        search=None,
        role="all",
    ):
        members = []

        if role in (
            "all",
            "owner",
        ):
            owner = organization.owner

            owner_matches_search = (
                not search
                or search.lower() in owner.full_name.lower()
                or search.lower() in owner.email.lower()
            )

            if owner_matches_search:
                members.append(
                    {
                        "id": owner.id,
                        "membership_id": None,
                        "name": owner.full_name,
                        "email": owner.email,
                        "avatar": owner.avatar,
                        "role": "owner",
                        "job_role": None,
                        "invited_by": None,
                        "joined_at": organization.created_at,
                        "project_count": 0,
                    }
                )

        if role == "owner":
            return members

        queryset = (
            OrganizationMember.objects.filter(
                organization=organization,
            )
            .select_related(
                "user",
                "job_role",
                "invited_by",
            )
            .order_by(
                "-joined_at",
            )
        )

        if search:
            queryset = queryset.filter(
                Q(
                    user__first_name__icontains=search,
                )
                | Q(
                    user__last_name__icontains=search,
                )
                | Q(
                    user__email__icontains=search,
                )
            )

        if role == "admin":
            queryset = queryset.filter(
                role="admin",
            )

        elif role == "member":
            queryset = queryset.filter(
                role="member",
            )

        for member in queryset:
            job_role = None

            if member.job_role:
                job_role = {
                    "id": member.job_role.id,
                    "name": member.job_role.name,
                }

            invited_by = None

            if member.invited_by:
                invited_by = {
                    "id": member.invited_by.id,
                    "name": member.invited_by.full_name,
                }

            members.append(
                {
                    "id": member.user.id,
                    "membership_id": member.id,
                    "name": member.user.full_name,
                    "email": member.user.email,
                    "avatar": member.user.avatar,
                    "role": member.role,
                    "job_role": job_role,
                    "invited_by": invited_by,
                    "joined_at": member.joined_at,
                    "project_count": 0,
                }
            )

        return members
