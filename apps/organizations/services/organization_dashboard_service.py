from apps.organizations.constants import (
    MOCK_ORGANIZATION_DASHBOARD_STATS,
)
from apps.organizations.models import Organization
from ..exceptions import OrganizationNotFoundException


class OrganizationDashboardService:

    @staticmethod
    def get_dashboard(
        *,
        user,
        slug: str,
    ) -> dict:

        organization = Organization.objects.filter(
            owner=user,
            slug=slug,
            deleted_at__isnull=True,
            is_archived=False,
        ).first()

        if organization is None:
            raise OrganizationNotFoundException("Organization not found.")

        if organization.owner_id != user.id:
            raise OrganizationNotFoundException("Organization not found.")

        stats = MOCK_ORGANIZATION_DASHBOARD_STATS

        return {
            "id": organization.id,
            "name": organization.name,
            "description": organization.description,
            "slug": organization.slug,
            "icon": organization.icon,
            "logo_url": organization.logo_url,
            "accent_color": organization.accent_color,
            "updated_at": organization.updated_at,
            "role": "owner",
            "total_projects": stats["total_projects"],
            "total_members": stats["total_members"],
            "active_sprints": stats["active_sprints"],
            "open_issues": stats["open_issues"],
            "completed_issues": stats["completed_issues"],
        }
