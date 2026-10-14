import json

from django.template.loader import render_to_string

from apps.ai.constants import SPRINT_SUMMARY_PROMPT
from apps.ai.serializers import AISprintSummaryResponseSerializer
from apps.ai.services.openrouter_service import OpenRouterService
from apps.projects.models import Issue, IssueSprintHistory


class SprintSummaryService:
    @staticmethod
    def _is_completed(issue):
        category = getattr(issue.status, "category", "")
        return str(category).lower() in {"done", "complete", "completed"}

    @classmethod
    def _get_sprint_issues(cls, sprint):
        return list(
            Issue.objects.filter(
                project=sprint.project, sprint=sprint, deleted_at__isnull=True
            ).select_related("project", "status", "assignee")
        )

    @staticmethod
    def _get_scope_changes(sprint):
        history = (
            IssueSprintHistory.objects.filter(
                issue__project=sprint.project, issue__deleted_at__isnull=True
            )
            .select_related("issue", "sprint")
            .order_by("issue_id", "moved_at", "id")
        )

        added = {}
        removed = {}

        target_sprint_id = sprint.id
        previous_sprint_by_issue = {}

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

        completed_issues = [issue for issue in issues if cls._is_completed(issue)]
        incomplete_issues = [issue for issue in issues if not cls._is_completed(issue)]

        total_story_points = sum(issue.story_points or 0 for issue in issues)
        completed_story_points = sum(
            issue.story_points or 0 for issue in completed_issues
        )

        total_issues = len(issues)
        completed_count = len(completed_issues)

        metrics = {
            "total_issues": total_issues,
            "completed_issues": completed_count,
            "incomplete_issues": len(incomplete_issues),
            "completion_percentage": (
                round(completed_count / total_issues * 100, 2) if total_issues else 0
            ),
            "total_story_points": total_story_points,
            "completed_story_points": completed_story_points,
        }

        scope_changes = cls._get_scope_changes(sprint)

        issue_details = [
            {
                "key": issue.key,
                "title": issue.title,
                "description": (issue.description or "")[:1000],
                "issue_type": issue.issue_type,
                "priority": issue.priority,
                "status": str(issue.status),
                "story_points": issue.story_points,
                "completed": cls._is_completed(issue),
            }
            for issue in issues
        ]

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
