from django.db.models import Count, Q
from ..models import Organization


class OrganizationQueryService:

    SORT_FIELDS = {
        "name": "name",
        "member": "member_count",
        "project": "project_count",
        "recent": "created_at",
    }

    @staticmethod
    def get_user_organizations(
        user,
        search: str | None = None,
        sort_by: str = "name",
        order: str = "asc",
    ):
        organizations = (
            Organization.objects.filter(
                Q(owner=user) | Q(members__user=user),
                is_archived=False,
                deleted_at__isnull=True,
            )
            .select_related("owner")
            .distinct()
        )

        if search:
            search = search.strip()
            if search:
                organizations = organizations.filter(
                    Q(name__icontains=search)
                    | Q(description__icontains=search)
                    | Q(slug__icontains=search)
                )

        organizations = organizations.annotate(
            member_count=Count(
                "members",
                distinct=True,
            ),
            project_count=Count(
                "projects",
                filter=Q(
                    projects__is_archived=False,
                    projects__deleted_at__isnull=True,
                ),
                distinct=True,
            ),
        )

        sort_field = OrganizationQueryService.SORT_FIELDS.get(
            sort_by,
            "name",
        )

        if order == "desc":
            sort_field = f"-{sort_field}"

        return organizations.order_by(
            "-is_pinned",
            sort_field,
            "id",
        )
