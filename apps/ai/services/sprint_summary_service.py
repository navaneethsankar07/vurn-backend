import json

from apps.ai.constants import SPRINT_SUMMARY_PROMPT
from apps.ai.serializers import AISprintSummaryResponseSerializer
from apps.ai.services.openrouter_service import OpenRouterService
from apps.projects.models import Issue, IssueSprintHistory


class SprintSummaryService:
    SUBTASK_TYPE = "subtask"

    @staticmethod
    def _is_subtask(issue):
        return str(issue.issue_type).lower() == SprintSummaryService.SUBTASK_TYPE

    @staticmethod
    def _is_completed(issue):
        category = getattr(issue.status, "category", "")
        return str(category).lower() in {"done", "complete", "completed"}

    @classmethod
    def _get_sprint_issues(cls, sprint):
        return list(
            Issue.objects.filter(
                project=sprint.project, sprint=sprint, deleted_at__isnull=True
            )
            .select_related("project", "status", "assignee", "parent", "parent__status")
            .order_by("id")
        )

    @classmethod
    def _serialize_issue(cls, issue, *, subtasks=None, in_sprint=True):
        return {
            "id": issue.id,
            "key": issue.key,
            "title": issue.title,
            "description": (issue.description or "")[:1000],
            "issue_type": str(issue.issue_type),
            "priority": str(issue.priority),
            "status": str(issue.status),
            "status_category": str(getattr(issue.status, "category", "")),
            "story_points": issue.story_points or 0,
            "completed": cls._is_completed(issue),
            "in_sprint": in_sprint,
            "subtasks": subtasks or [],
        }

    @classmethod
    def _build_issue_details(cls, sprint, issues):
        """
        Build top-level sprint issues with subtasks nested underneath.
        A parent outside the sprint is included as context when one of its
        subtasks is in the sprint, but it does not affect sprint metrics.
        """
        sprint_issue_ids = {issue.id for issue in issues}
        top_level_issues = [issue for issue in issues if not cls._is_subtask(issue)]
        subtasks = [issue for issue in issues if cls._is_subtask(issue)]

        subtasks_by_parent = {}
        for subtask in subtasks:
            if subtask.parent_id:
                subtasks_by_parent.setdefault(subtask.parent_id, []).append(subtask)

        missing_parent_ids = {
            subtask.parent_id
            for subtask in subtasks
            if subtask.parent_id and subtask.parent_id not in sprint_issue_ids
        }

        external_parents = {
            issue.id: issue
            for issue in Issue.objects.filter(
                id__in=missing_parent_ids,
                project=sprint.project,
                deleted_at__isnull=True,
            ).select_related("project", "status", "assignee")
        }

        result = []

        for issue in top_level_issues:
            child_details = [
                cls._serialize_issue(child)
                for child in subtasks_by_parent.get(issue.id, [])
            ]

            result.append(cls._serialize_issue(issue, subtasks=child_details))

        for parent_id, children in subtasks_by_parent.items():
            if parent_id in sprint_issue_ids:
                continue

            parent = external_parents.get(parent_id)
            if parent is None:
                for child in children:
                    result.append(
                        {
                            "parent": {
                                "id": parent_id,
                                "key": None,
                                "title": "Parent issue unavailable",
                            },
                            "subtask": cls._serialize_issue(child),
                        }
                    )
                continue

            result.append(
                {
                    **cls._serialize_issue(
                        parent,
                        subtasks=[cls._serialize_issue(child) for child in children],
                        in_sprint=False,
                    ),
                    "context_only": True,
                }
            )

        return result

    @classmethod
    def _get_scope_changes(cls, sprint):
        history = (
            IssueSprintHistory.objects.filter(
                issue__project=sprint.project, issue__deleted_at__isnull=True
            )
            .exclude(issue__issue_type=cls.SUBTASK_TYPE)
            .select_related("issue", "sprint")
            .order_by("issue_id", "moved_at", "id")
        )

        added = {}
        removed = {}
        previous_sprint_by_issue = {}
        target_sprint_id = sprint.id

        for entry in history:
            issue_id = entry.issue_id
            previous_sprint_id = previous_sprint_by_issue.get(issue_id)
            current_sprint_id = entry.sprint_id

            if current_sprint_id == target_sprint_id:
                if previous_sprint_id != target_sprint_id:
                    added[issue_id] = entry.issue
                removed.pop(issue_id, None)

            elif previous_sprint_id == target_sprint_id:
                removed[issue_id] = entry.issue
                added.pop(issue_id, None)

            previous_sprint_by_issue[issue_id] = current_sprint_id

        added_issues = list(added.values())
        removed_issues = list(removed.values())

        return {
            "issues_added": len(added_issues),
            "issues_removed": len(removed_issues),
            "added_issue_keys": sorted(issue.key for issue in added_issues),
            "removed_issue_keys": sorted(issue.key for issue in removed_issues),
        }

    @classmethod
    def generate(cls, *, sprint):
        issues = cls._get_sprint_issues(sprint)

        top_level_issues = [issue for issue in issues if not cls._is_subtask(issue)]

        completed_issues = [
            issue for issue in top_level_issues if cls._is_completed(issue)
        ]
        incomplete_issues = [
            issue for issue in top_level_issues if not cls._is_completed(issue)
        ]

        total_issues = len(top_level_issues)
        completed_count = len(completed_issues)

        metrics = {
            "total_issues": total_issues,
            "completed_issues": completed_count,
            "incomplete_issues": len(incomplete_issues),
            "completion_percentage": (
                round(completed_count / total_issues * 100, 2) if total_issues else 0
            ),
            "total_story_points": sum(
                issue.story_points or 0 for issue in top_level_issues
            ),
            "completed_story_points": sum(
                issue.story_points or 0 for issue in completed_issues
            ),
        }

        scope_changes = cls._get_scope_changes(sprint)
        issue_details = cls._build_issue_details(sprint, issues)

        sprint_context = {
            "sprint": {
                "id": sprint.id,
                "name": sprint.name,
                "goal": sprint.goal,
                "description": sprint.description,
                "start_date": sprint.start_date.isoformat(),
                "end_date": sprint.end_date.isoformat(),
                "estimated_days": sprint.estimated_days,
                "status": sprint.status,
            },
            "metrics": metrics,
            "scope_changes": scope_changes,
            "issues": issue_details,
        }

        ai_result = OpenRouterService.generate_json(
            messages=[
                {"role": "system", "content": SPRINT_SUMMARY_PROMPT},
                {"role": "user", "content": json.dumps(sprint_context)},
            ],
            serializer_class=AISprintSummaryResponseSerializer,
            temperature=0.2,
            max_tokens=1800,
        )

        return {
            "sprint": sprint_context["sprint"],
            "metrics": {
                **metrics,
                "issues_added": scope_changes["issues_added"],
                "issues_removed": scope_changes["issues_removed"],
                "added_issue_keys": scope_changes["added_issue_keys"],
                "removed_issue_keys": scope_changes["removed_issue_keys"],
            },
            **ai_result,
        }
