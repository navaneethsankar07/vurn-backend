from django.core import signing
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project

from ..services.github_connection_service import GitHubConnectionService


class GitHubConnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, organization_slug, project_slug):
        project = (
            Project.objects.select_related("organization")
            .filter(
                organization__slug=organization_slug,
                slug=project_slug,
                deleted_at__isnull=True,
                is_archived=False,
            )
            .first()
        )

        if project is None:
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )

        authorization_url = GitHubConnectionService.create_installation_url(
            project=project, user=request.user
        )

        return Response(
            {"authorization_url": authorization_url}, status=status.HTTP_200_OK
        )


class GitHubInstallationCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = request.query_params.get("state")
        installation_id = request.query_params.get("installation_id")
        setup_action = request.query_params.get("setup_action")

        if not state or not installation_id:
            return Response(
                {"detail": ("Missing GitHub installation parameters.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            integration, installation = (
                GitHubConnectionService.handle_installation_callback(
                    user=request.user,
                    state=state,
                    installation_id=installation_id,
                    setup_action=setup_action,
                )
            )
        except signing.BadSignature:
            return Response(
                {"detail": "Invalid or expired installation state."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": ("GitHub App installed successfully."),
                "integration_id": integration.id,
                "provider": integration.provider,
                "account": {
                    "login": installation["account_login"],
                    "type": installation["account_type"],
                },
            },
            status=status.HTTP_200_OK,
        )
