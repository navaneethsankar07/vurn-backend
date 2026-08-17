from django.db.models import Q, Case, When, Value, IntegerField

from apps.organizations.models import Organization
from apps.organizations.constants import MOCK_ORGANIZATION_STATS


class OrganizationQueryService:

    SORT_FIELDS = {
        "name": "name",
        "member": "mock_member_count",
        "project": "mock_project_count",
        "recent": "created_at",
    }

    @staticmethod
    def get_user_organizations(
        user,
        search: str | None = None,
        sort_by: str = "name",
        order: str = "asc",
    ):
        organizations = Organization.objects.filter(
            owner=user,
            is_archived=False,
            deleted_at__isnull=True,
        ).select_related("owner")

        if search:
            search = search.strip()

            if search:
                organizations = organizations.filter(
                    Q(name__icontains=search)
                    | Q(description__icontains=search)
                    | Q(slug__icontains=search)
                )

        member_cases = [
            When(
                id=organization_id,
                then=Value(
                    stats["member_count"],
                ),
            )
            for organization_id, stats
            in MOCK_ORGANIZATION_STATS.items()
        ]

        project_cases = [
            When(
                id=organization_id,
                then=Value(
                    stats["project_count"],
                ),
            )
            for organization_id, stats
            in MOCK_ORGANIZATION_STATS.items()
        ]

        organizations = organizations.annotate(
            mock_member_count=Case(
                *member_cases,
                default=Value(1),
                output_field=IntegerField(),
            ),
            mock_project_count=Case(
                *project_cases,
                default=Value(0),
                output_field=IntegerField(),
            ),
        )

        sort_field = OrganizationQueryService.SORT_FIELDS.get(
            sort_by,
            "name",
        )

        if order == "desc":
            sort_field = f"-{sort_field}"

        organizations = organizations.order_by(
            sort_field,
            "id",
        )

        return organizations