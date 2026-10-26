from django.db import IntegrityError, transaction

from apps.projects.models import Issue

from ..exceptions import (
    GitIssueAlreadyLinkedException,
    GitIssueAutoMatchException,
    GitIssueClosedException,
    GitIssueLinkLimitException,
    GitRepositoryException,
)
from ..models import GitIssue, GitIssueWorkItem
from .repository_service import GitRepositoryService


class GitIssueLinkService:
    @classmethod
    @transaction.atomic
    def link_work_item(
        cls, *, project, repository_id, git_issue_id, issue_id=None, auto_match=False
    ):
        integration = GitRepositoryService._get_github_integration(project=project)

        git_issue = (
            GitIssue.objects.select_for_update()
            .filter(
                id=git_issue_id,
                repository__id=repository_id,
                repository__integration=integration,
            )
            .first()
        )

        if git_issue is None:
            raise GitRepositoryException("GitHub issue not found.")

        if git_issue.state == "closed":
            raise GitIssueClosedException(
                "Cannot link a closed GitHub issue to a work item."
            )

        existing_link = (
            GitIssueWorkItem.objects.select_related("issue")
            .filter(git_issue=git_issue)
            .first()
        )

        if existing_link is not None:
            if issue_id is not None and existing_link.issue_id == issue_id:
                return existing_link, "manual"

            if auto_match:
                return existing_link, "existing"

            raise GitIssueAlreadyLinkedException("This GitHub issue is already linked.")

        if auto_match:
            matches = list(
                Issue.objects.select_for_update().filter(
                    project=project,
                    deleted_at__isnull=True,
                    title__iexact=git_issue.title,
                )[:2]
            )

            if len(matches) != 1:
                raise GitIssueAutoMatchException(
                    "Could not find exactly one matching work item. "
                    "Please select a work item manually."
                )

            work_item = matches[0]
            matched_by = "title"
        else:
            work_item = (
                Issue.objects.select_for_update()
                .filter(id=issue_id, project=project, deleted_at__isnull=True)
                .first()
            )

            if work_item is None:
                raise GitIssueAutoMatchException("Work item not found in this project.")

            matched_by = "manual"

        linked_count = GitIssueWorkItem.objects.filter(issue=work_item).count()

        if linked_count >= 5:
            raise GitIssueLinkLimitException(
                "A work item can have a maximum of 5 linked GitHub issues."
            )

        try:
            link = GitIssueWorkItem.objects.create(git_issue=git_issue, issue=work_item)
        except IntegrityError as exc:
            raise GitIssueAlreadyLinkedException(
                "This GitHub issue is already linked."
            ) from exc

        return link, matched_by
