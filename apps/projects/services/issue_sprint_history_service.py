from ..models import IssueSprintHistory


class IssueSprintHistoryService:

    @staticmethod
    def list_history(*, issue):
        return (
            IssueSprintHistory.objects.filter(issue=issue)
            .select_related("sprint")
            .order_by("moved_at", "id")
        )

    @staticmethod
    def create_history(*, issue, sprint):
        return IssueSprintHistory.objects.create(issue=issue, sprint=sprint)

    @staticmethod
    def create_backlog_history(*, issue):
        return IssueSprintHistory.objects.create(issue=issue, sprint=None)

    @staticmethod
    def create_history_bulk(*, issues, sprint):
        IssueSprintHistory.objects.bulk_create(
            [IssueSprintHistory(issue=issue, sprint=sprint) for issue in issues]
        )

    @staticmethod
    def create_backlog_history_bulk(*, issues):
        IssueSprintHistory.objects.bulk_create(
            [IssueSprintHistory(issue=issue, sprint=None) for issue in issues]
        )
