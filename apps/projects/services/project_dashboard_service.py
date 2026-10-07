from apps.projects.models import Issue, Sprint


class ProjectDashboardService:

    @staticmethod
    def get_project_details(*, project) -> dict:
        open_issue_count = (
            Issue.objects.filter(project=project, deleted_at__isnull=True)
            .exclude(status__category="backlog")
            .exclude(status__category="done")
            .count()
        )

        completed_issue_count = Issue.objects.filter(
            project=project, deleted_at__isnull=True, status__category="done"
        ).count()

        active_sprint = (
            Sprint.objects.filter(project=project, status="active")
            .order_by("-created_at")
            .first()
        )

        return {
            "name": project.name,
            "key": project.key,
            "status": project.status,
            "description": project.description,
            "open_issues": open_issue_count,
            "completed_issues": completed_issue_count,
            "active_sprint": active_sprint,
        }
