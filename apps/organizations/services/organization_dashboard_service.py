from ..constants import (
    MOCK_ORGANIZATION_DASHBOARD_STATS,
)
from .organization_access_service import (
    OrganizationAccessService,
)
from .organization_service import (
    OrganizationService,
)


class OrganizationDashboardService:

    @staticmethod
    def get_dashboard(
        *,
        user,
        slug: str,
    ) -> dict:

        organization = OrganizationService.get_user_organization(
            user=user,
            slug=slug,
        )

        access = OrganizationAccessService.get_user_access(
            organization=organization,
            user=user,
        )

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
            "role": access["role"],
            "permissions": access["permissions"],
            "total_projects": stats["total_projects"],
            "total_members": stats["total_members"],
            "active_sprints": stats["active_sprints"],
            "open_issues": stats["open_issues"],
            "completed_issues": stats["completed_issues"],
        }
