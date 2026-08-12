from apps.organizations.constants import (
    MOCK_ORGANIZATION_STATS,
)
from apps.organizations.models import Organization


class OrganizationQueryService:

    @staticmethod
    def get_user_organizations(
        user,
    ) -> dict:

        organizations = Organization.objects.filter(
            owner=user,
            deleted_at__isnull=True,
        ).select_related("owner")

        organization_data = []

        for organization in organizations:

            stats = MOCK_ORGANIZATION_STATS.get(
                organization.id,
                {
                    "member_count": 1,
                    "project_count": 0,
                },
            )

            organization_data.append(
                {
                    "id": organization.id,
                    "name": organization.name,
                    "description": organization.description,
                    "slug": organization.slug,
                    "icon": organization.icon,
                    "accent_color": organization.accent_color,
                    "logo_url": organization.logo_url,
                    "role": "owner",
                    "member_count": stats["member_count"],
                    "project_count": stats["project_count"],
                    "last_opened_at": None,
                    "is_pinned": False,
                }
            )

        return {
            "recent": [],
            "pinned": [],
            "organizations": organization_data,
        }
