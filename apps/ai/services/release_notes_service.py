from datetime import datetime, time, timedelta

from django.utils import timezone

from ..constants import RELEASE_NOTES_PROMPT
from ..serializers import AIReleaseNotesResponseSerializer
from .openrouter_service import OpenRouterService
from apps.integrations.models import (
    GitCommit,
    GitCommitIssue,
    GitIntegration,
    GitPullRequest,
    GitPullRequestIssue,
    GitRepository,
)


class ReleaseNotesService:
    MAX_COMMITS = 100
    MAX_PULL_REQUESTS = 50

    @staticmethod
    def _date_bounds(start_date, end_date):
        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date + timedelta(days=1), time.min)

        if timezone.is_naive(timezone.now()):
            return start, end

        return (
            timezone.make_aware(start, timezone.get_current_timezone()),
            timezone.make_aware(end, timezone.get_current_timezone()),
        )

    @staticmethod
    def _serialize_linked_issues(linked_issues):
        return [
            {
                "key": issue.key,
                "title": issue.title,
                "status": str(issue.status),
                "issue_type": str(issue.issue_type),
            }
            for issue in linked_issues
        ]

    @classmethod
    def _get_commit_data(cls, repository, start, end):
        commits = list(
            GitCommit.objects.filter(
                repository=repository, committed_at__gte=start, committed_at__lt=end
            ).order_by("-committed_at")[: cls.MAX_COMMITS]
        )

        commit_ids = [commit.id for commit in commits]
        linked_by_commit = {}

        links = GitCommitIssue.objects.filter(
            commit_id__in=commit_ids, issue__deleted_at__isnull=True
        ).select_related("issue", "issue__status")

        for link in links:
            linked_by_commit.setdefault(link.commit_id, []).append(link.issue)

        return [
            {
                "sha": commit.sha[:12],
                "message": commit.message[:1500],
                "branch": commit.branch,
                "committed_at": commit.committed_at.isoformat(),
                "url": commit.url,
                "linked_issues": cls._serialize_linked_issues(
                    linked_by_commit.get(commit.id, [])
                ),
            }
            for commit in commits
        ]

    @classmethod
    def _get_pull_request_data(cls, repository, start, end):
        pull_requests = list(
            GitPullRequest.objects.filter(
                repository=repository,
                state="merged",
                merged_at__gte=start,
                merged_at__lt=end,
            ).order_by("-merged_at")[: cls.MAX_PULL_REQUESTS]
        )

        pull_request_ids = [pr.id for pr in pull_requests]
        linked_by_pr = {}

        links = GitPullRequestIssue.objects.filter(
            pull_request_id__in=pull_request_ids, issue__deleted_at__isnull=True
        ).select_related("issue", "issue__status")

        for link in links:
            linked_by_pr.setdefault(link.pull_request_id, []).append(link.issue)

        return [
            {
                "number": pr.pr_number,
                "title": pr.title,
                "description": pr.description[:2000],
                "author": pr.author_username,
                "source_branch": pr.source_branch,
                "target_branch": pr.target_branch,
                "merged_at": pr.merged_at.isoformat(),
                "url": pr.url,
                "linked_issues": cls._serialize_linked_issues(
                    linked_by_pr.get(pr.id, [])
                ),
            }
            for pr in pull_requests
        ]

    @classmethod
    def generate(cls, *, repository, start_date, end_date):
        start, end = cls._date_bounds(start_date, end_date)

        commits = cls._get_commit_data(repository, start, end)
        pull_requests = cls._get_pull_request_data(repository, start, end)

        if not commits and not pull_requests:
            return {
                "release_notes": {
                    "title": f"{repository.name} Release Notes",
                    "overview": (
                        "No commits or merged pull requests were found "
                        "in the selected reporting period."
                    ),
                    "highlights": [],
                    "bug_fixes": [],
                    "improvements": [],
                    "breaking_changes": [],
                    "known_issues": [],
                    "technical_changes": [],
                    "markdown": (
                        f"# {repository.name} Release Notes\n\n"
                        "No commits or merged pull requests were found "
                        "in the selected reporting period."
                    ),
                },
                "source_summary": {
                    "commits_analyzed": 0,
                    "merged_pull_requests_analyzed": 0,
                },
            }

        context = {
            "repository": {
                "name": repository.full_name,
                "description": repository.description,
                "default_branch": repository.default_branch,
            },
            "reporting_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "commits": commits,
            "merged_pull_requests": pull_requests,
        }

        ai_result = OpenRouterService.generate_json(
            messages=[
                {"role": "system", "content": RELEASE_NOTES_PROMPT},
                {"role": "user", "content": __import__("json").dumps(context)},
            ],
            serializer_class=AIReleaseNotesResponseSerializer,
            temperature=0.2,
            max_tokens=3500,
        )

        # Only allow references that actually exist in the supplied data.
        valid_references = {f"PR #{pr['number']}" for pr in pull_requests}
        for source in [*commits, *pull_requests]:
            for issue in source["linked_issues"]:
                valid_references.add(issue["key"])

        ai_result["highlights"] = [
            {
                **highlight,
                "references": [
                    ref for ref in highlight["references"] if ref in valid_references
                ],
            }
            for highlight in ai_result["highlights"]
        ]

        return {
            "release_notes": ai_result,
            "source_summary": {
                "commits_analyzed": len(commits),
                "merged_pull_requests_analyzed": len(pull_requests),
            },
        }
