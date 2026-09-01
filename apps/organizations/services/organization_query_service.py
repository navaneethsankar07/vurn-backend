from django.db.models import (
    Case,
    Count,
    IntegerField,
    Q,
    Value,
    When,
)

from ..constants import MOCK_ORGANIZATION_STATS
from ..models import Organization


class OrganizationQueryService:

    SORT_FIELDS = {
        "name": "name",
        "member": "member_count",
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

        project_cases = [
            When(
                id=organization_id,
                then=Value(
                    stats["project_count"],
                ),
            )
            for organization_id, stats in MOCK_ORGANIZATION_STATS.items()
        ]

        organizations = organizations.annotate(
            member_count=Count(
                "members",
                distinct=True,
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

        return organizations.order_by(
            sort_field,
            "id",
        )
