from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService
from apps.projects.services.project_service import ProjectService

from ..serializers import (
    GitHubRepositorySerializer,
    GitHubIntegrationStatusSerializer,
    GitHubRepositoryOverviewSerializer,
    GitHubRepositoryConnectionSerializer,
)

from ..exceptions import GitRepositoryAlreadyConnectedException, GitRepositoryException

from ..services.repository_service import GitRepositoryService


class GitHubRepositoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organization_slug, project_slug):
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

        ProjectAccessService.validate_project_edit_access(
            project=project, user=request.user
        )

        repositories = GitRepositoryService.get_available_repositories(project=project)

        serializer = GitHubRepositorySerializer(repositories, many=True)

        return Response({"repositories": serializer.data}, status=status.HTTP_200_OK)


class GitHubRepositoryOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organization_slug, project_slug, repository_id):
        project = ProjectService.get_project(
            organization_slug=organization_slug, project_slug=project_slug
        )

        ProjectAccessService.validate_project_view_access(
            project=project, user=request.user
        )

        try:
            repository = GitRepositoryService.get_repository_overview(
                project=project, repository_id=repository_id
            )
        except GitRepositoryException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = GitHubRepositoryOverviewSerializer(repository)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GitHubRepositoryConnectionView(APIView):
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

        ProjectAccessService.validate_project_edit_access(
            project=project, user=request.user
        )

        serializer = GitHubRepositoryConnectionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            repository = GitRepositoryService.connect_repository(
                project=project,
                repository_id=serializer.validated_data["repository_id"],
            )
        except GitRepositoryAlreadyConnectedException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(
            {
                "message": ("GitHub repository connected successfully."),
                "repository": {
                    "id": repository.id,
                    "external_repository_id": (repository.external_repository_id),
                    "name": repository.name,
                    "full_name": repository.full_name,
                    "repository_url": (repository.repository_url),
                    "default_branch": (repository.default_branch),
                    "visibility": repository.visibility,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class GitHubIntegrationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organization_slug, project_slug):
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

        ProjectAccessService.validate_project_edit_access(
            project=project, user=request.user
        )

        integration_status = GitRepositoryService.get_github_integration_status(
            project=project
        )

        serializer = GitHubIntegrationStatusSerializer(integration_status)

        return Response(serializer.data, status=status.HTTP_200_OK)
