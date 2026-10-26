from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Issue


class RecentActivityService:
    @staticmethod
    def get_recent_activity(*, user):
        assigned_issues = list(
            Issue.objects.filter(
                assignee=user,
                deleted_at__isnull=True,
                project__deleted_at__isnull=True,
                project__organization__deleted_at__isnull=True,
            )
            .select_related("status", "project", "project__organization")
            .order_by("-updated_at", "-created_at")[:3]
        )

        remaining = 3 - len(assigned_issues)
        recent_issues = assigned_issues.copy()

        if remaining > 0:
            assigned_ids = [issue.id for issue in assigned_issues]

            created_issues = (
                Issue.objects.filter(
                    reporter=user,
                    deleted_at__isnull=True,
                    project__deleted_at__isnull=True,
                    project__organization__deleted_at__isnull=True,
                )
                .exclude(id__in=assigned_ids)
                .select_related("status", "project", "project__organization")
                .order_by("-created_at")[:remaining]
            )

            recent_issues.extend(created_issues)

        issue_data = [
            {
                "id": issue.id,
                "key": issue.key,
                "title": issue.title,
                "status": issue.status.name,
                "status_category": issue.status.category,
                "priority": issue.priority,
                "issue_type": issue.issue_type,
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
                "project_slug": issue.project.slug,
                "project_name": issue.project.name,
                "organization_slug": issue.project.organization.slug,
                "organization_name": issue.project.organization.name,
            }
            for issue in recent_issues
        ]

        owned_organizations = Organization.objects.filter(
            owner=user, deleted_at__isnull=True
        ).values("id", "name", "slug", "icon", "accent_color", "created_at")

        memberships = OrganizationMember.objects.filter(
            user=user, organization__deleted_at__isnull=True
        ).select_related("organization")

        organization_events = [
            {
                "organization": organization,
                "event_type": "created",
                "event_date": organization["created_at"],
            }
            for organization in owned_organizations
        ]

        organization_events.extend(
            {
                "organization": {
                    "id": membership.organization.id,
                    "name": membership.organization.name,
                    "slug": membership.organization.slug,
                    "icon": membership.organization.icon,
                    "accent_color": membership.organization.accent_color,
                    "created_at": membership.organization.created_at,
                },
                "event_type": (
                    "created"
                    if membership.organization.owner_id == user.id
                    else "joined"
                ),
                "event_date": (
                    membership.organization.created_at
                    if membership.organization.owner_id == user.id
                    else membership.joined_at
                ),
            }
            for membership in memberships
        )

        seen_ids = set()
        unique_organization_events = []
        for event in sorted(
            organization_events, key=lambda x: x["event_date"], reverse=True
        ):
            org_id = (
                event["organization"]["id"]
                if isinstance(event["organization"], dict)
                else event["organization"]["id"]
            )
            if org_id not in seen_ids:
                seen_ids.add(org_id)
                unique_organization_events.append(event)

        latest_organizations = unique_organization_events[:3]

        organization_data = [
            {
                "id": (
                    item["organization"]["id"]
                    if isinstance(item["organization"], dict)
                    else item["organization"]["id"]
                ),
                "name": (
                    item["organization"]["name"]
                    if isinstance(item["organization"], dict)
                    else item["organization"]["name"]
                ),
                "slug": (
                    item["organization"]["slug"]
                    if isinstance(item["organization"], dict)
                    else item["organization"]["slug"]
                ),
                "icon": (
                    item["organization"]["icon"]
                    if isinstance(item["organization"], dict)
                    else item["organization"]["icon"]
                ),
                "accent_color": (
                    item["organization"]["accent_color"]
                    if isinstance(item["organization"], dict)
                    else item["organization"]["accent_color"]
                ),
                "event_type": item["event_type"],
                "event_date": item["event_date"],
            }
            for item in latest_organizations
        ]

        return {"recent_issues": issue_data, "recent_organizations": organization_data}
