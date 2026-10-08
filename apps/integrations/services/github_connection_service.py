import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.core import signing
from django.db import transaction

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService

from ..constants import STATE_MAX_AGE, STATE_SALT
from ..models import GitIntegration, GitProviderInstallation
from ..providers.github.authentication import GitHubAuthenticationService


class GitHubConnectionService:

    @classmethod
    def create_installation_url(cls, *, project, user):
        ProjectAccessService.validate_project_edit_access(project=project, user=user)

        state = signing.dumps(
            {
                "project_id": project.id,
                "user_id": user.id,
                "nonce": secrets.token_urlsafe(16),
            },
            salt=cls.STATE_SALT,
        )

        query_string = urlencode({"state": state})

        return (
            f"https://github.com/apps/"
            f"{settings.GITHUB_APP_SLUG}/installations/new"
            f"?{query_string}"
        )

    @classmethod
    @transaction.atomic
    def handle_installation_callback(
        cls, *, user, state, installation_id, setup_action
    ):
        payload = signing.loads(state, salt=STATE_SALT, max_age=STATE_MAX_AGE)

        if payload["user_id"] != user.id:
            raise ValueError("GitHub installation state does not belong to this user.")

        project = (
            Project.objects.select_related("organization")
            .filter(
                id=payload["project_id"], deleted_at__isnull=True, is_archived=False
            )
            .first()
        )

        if project is None:
            raise ValueError(
                "Project associated with the GitHub installation " "was not found."
            )

        ProjectAccessService.validate_project_edit_access(project=project, user=user)

        installation = GitHubAuthenticationService.get_installation_details(
            installation_id=installation_id
        )

        integration, _ = GitIntegration.objects.update_or_create(
            project=project,
            provider="github",
            defaults={"status": "active", "connected_by": user},
        )

        GitProviderInstallation.objects.update_or_create(
            integration=integration,
            defaults={
                "provider": "github",
                "external_installation_id": str(installation["installation_id"]),
                "account_login": installation["account_login"] or "",
                "account_type": installation["account_type"] or "",
            },
        )

        return integration, installation
