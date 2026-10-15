from apps.recent_activities.models import RecentActivity


class RecentActivityService:
    @staticmethod
    def create_activity(
        *,
        organization,
        activity_type,
        description,
        actor=None,
        project=None,
        sprint=None,
        issue=None,
        metadata=None
    ):
        return RecentActivity.objects.create(
            organization=organization,
            project=project,
            sprint=sprint,
            issue=issue,
            actor=actor,
            activity_type=activity_type,
            description=description,
            metadata=metadata or {},
        )

    @staticmethod
    def get_organization_activities(*, organization):
        return (
            RecentActivity.objects.filter(organization=organization)
            .select_related("actor", "project", "sprint", "issue")
            .order_by("-created_at")
        )

    @staticmethod
    def get_project_activities(*, project):
        return (
            RecentActivity.objects.filter(project=project)
            .select_related("actor", "project", "sprint", "issue")
            .order_by("-created_at")
        )

    @staticmethod
    def get_sprint_activities(*, sprint):
        return (
            RecentActivity.objects.filter(sprint=sprint)
            .select_related("actor", "project", "sprint", "issue")
            .order_by("-created_at")
        )
