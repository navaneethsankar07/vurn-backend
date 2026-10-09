from django.db import transaction
from django.utils import timezone

from apps.integrations.models import GitCommit, GitIssue, GitPullRequest
from apps.integrations.models import GitRepository, GitWebhookDelivery


class GitHubWebhookProcessor:
    @classmethod
    def process_delivery(cls, *, delivery):
        try:
            with transaction.atomic():
                cls._dispatch_event(delivery=delivery)

                delivery.status = "processed"
                delivery.error_message = None
                delivery.processed_at = timezone.now()
                delivery.save(update_fields=["status", "error_message", "processed_at"])
        except Exception as exc:
            delivery.status = "failed"
            delivery.error_message = str(exc)
            delivery.processed_at = timezone.now()
            delivery.save(update_fields=["status", "error_message", "processed_at"])
            raise

    @classmethod
    def _dispatch_event(cls, *, delivery):
        payload = delivery.payload
        event_type = delivery.event_type

        repository_data = payload.get("repository") or {}
        external_repository_id = repository_data.get("id")

        if not external_repository_id:
            raise ValueError("Webhook payload has no repository ID.")

        repository = GitRepository.objects.filter(
            integration=delivery.integration,
            external_repository_id=str(external_repository_id),
        ).first()

        if repository is None:
            raise ValueError("Repository is not connected to this VURN integration.")

        if event_type == "push":
            cls._sync_commits(repository=repository, payload=payload)
        elif event_type == "pull_request":
            cls._sync_pull_request(repository=repository, payload=payload)
        elif event_type == "issues":
            cls._sync_issue(repository=repository, payload=payload)
        else:
            return

    @staticmethod
    def _sync_commits(*, repository, payload):
        ref = payload.get("ref") or ""
        branch = ref.removeprefix("refs/heads/")

        for commit_data in payload.get("commits", []):
            sha = commit_data.get("id")

            if not sha:
                continue

            author = commit_data.get("author") or {}
            timestamp = commit_data.get("timestamp")

            GitCommit.objects.update_or_create(
                repository=repository,
                sha=sha,
                defaults={
                    "message": commit_data.get("message") or "",
                    "author_name": author.get("name") or "",
                    "author_email": author.get("email") or "",
                    "branch": branch,
                    "url": commit_data.get("url") or "",
                    "committed_at": timestamp,
                },
            )

        repository.last_synced_at = timezone.now()
        repository.save(update_fields=["last_synced_at"])

    @staticmethod
    def _sync_pull_request(*, repository, payload):
        pull_request = payload.get("pull_request")

        if not pull_request:
            raise ValueError("Pull request event has no pull request data.")

        action = payload.get("action")

        if action == "deleted":
            return

        merged_at = pull_request.get("merged_at")
        closed_at = pull_request.get("closed_at")

        if merged_at:
            state = "merged"
        elif pull_request.get("state") == "closed":
            state = "closed"
        else:
            state = "open"

        user = pull_request.get("user") or {}
        head = pull_request.get("head") or {}
        base = pull_request.get("base") or {}

        GitPullRequest.objects.update_or_create(
            repository=repository,
            pr_number=pull_request["number"],
            defaults={
                "external_id": pull_request["id"],
                "title": pull_request.get("title") or "",
                "description": pull_request.get("body") or "",
                "state": state,
                "author_username": user.get("login") or "",
                "source_branch": head.get("ref") or "",
                "target_branch": base.get("ref") or "",
                "url": pull_request.get("html_url") or "",
                "opened_at": pull_request.get("created_at"),
                "merged_at": merged_at,
                "closed_at": closed_at,
                "draft": pull_request.get("draft", False),
            },
        )

    @staticmethod
    def _sync_issue(*, repository, payload):
        github_issue = payload.get("issue")

        if not github_issue:
            raise ValueError("Issues event has no issue data.")

        if "pull_request" in github_issue:
            return

        action = payload.get("action")

        if action == "deleted":
            GitIssue.objects.filter(
                repository=repository, issue_number=github_issue["number"]
            ).delete()
            return

        user = github_issue.get("user") or {}

        GitIssue.objects.update_or_create(
            repository=repository,
            issue_number=github_issue["number"],
            defaults={
                "external_id": github_issue["id"],
                "title": github_issue.get("title") or "",
                "description": github_issue.get("body") or "",
                "state": github_issue.get("state") or "open",
                "author_username": user.get("login") or "",
                "url": github_issue.get("html_url") or "",
                "opened_at": github_issue.get("created_at"),
                "closed_at": github_issue.get("closed_at"),
                "created_at": github_issue.get("created_at"),
                "updated_at": github_issue.get("updated_at"),
            },
        )
