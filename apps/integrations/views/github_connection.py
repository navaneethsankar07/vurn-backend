from django.core import signing
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project

from ..services.github_connection_service import GitHubConnectionService
from ..serializers import GitHubInstallationCompleteSerializer


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


class GitHubInstallationCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GitHubInstallationCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization_slug = None
        project_slug = None

        try:
            project = GitHubConnectionService.get_project_from_state(
                user=request.user, state=serializer.validated_data["state"]
            )

            organization_slug = project.organization.slug
            project_slug = project.slug

            project, integration, installation = (
                GitHubConnectionService.handle_installation_callback(
                    user=request.user,
                    state=serializer.validated_data["state"],
                    installation_id=(serializer.validated_data["installation_id"]),
                    setup_action=(serializer.validated_data["setup_action"]),
                )
            )

        except signing.BadSignature:
            return Response(
                {
                    "detail": ("Invalid or expired GitHub installation state."),
                    "organization_slug": organization_slug,
                    "project_slug": project_slug,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                    "organization_slug": organization_slug,
                    "project_slug": project_slug,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "GitHub App installed successfully.",
                "integration_id": integration.id,
                "provider": integration.provider,
                "organization_slug": project.organization.slug,
                "project_slug": project.slug,
                "account": {
                    "login": installation["account_login"],
                    "type": installation["account_type"],
                },
            },
            status=status.HTTP_200_OK,
        )
