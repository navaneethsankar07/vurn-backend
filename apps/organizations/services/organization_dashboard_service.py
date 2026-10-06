from apps.projects.models import Issue, Sprint

from .organization_access_service import OrganizationAccessService
from .organization_service import OrganizationService


class OrganizationDashboardService:

    @staticmethod
    def get_dashboard(*, user, slug: str) -> dict:

        organization = OrganizationService.get_user_organization(user=user, slug=slug)
        access = OrganizationAccessService.get_user_access(
            organization=organization, user=user
        )
        latest_projects = organization.projects.filter(
            deleted_at__isnull=True, is_archived=False
        ).order_by("-updated_at")[:4]
        total_projects = organization.projects.count()
        total_members = organization.members.count() + 1  # Including the owner
        completed_issues = Issue.objects.filter(
            project__organization=organization,
            deleted_at__isnull=True,
            status__category="done",
        ).count()
        open_issue_count = (
            Issue.objects.filter(
                project__organization=organization, deleted_at__isnull=True
            )
            .exclude(status__category="backlog")
            .count()
        )
        active_sprints_queryset = Sprint.objects.filter(
            project__organization=organization, status="active"
        ).select_related("project")
        active_sprint_count = active_sprints_queryset.count()
        active_sprints = active_sprints_queryset.order_by("-created_at")[:5]

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
            "total_projects": total_projects,
            "total_members": total_members,
            "completed_issues": completed_issues,
            "active_sprints": active_sprints,
            "active_sprint_count": active_sprint_count,
            "open_issues": open_issue_count,
            "latest_projects": latest_projects,
        }
