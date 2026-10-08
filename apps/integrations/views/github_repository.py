from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService

from ..serializers import (
    GitHubRepositorySerializer,
    GitHubRepositoryConnectionSerializer,
)

from ..exceptions import GitRepositoryAlreadyConnectedException

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

        repositories = GitRepositoryService.get_available_repositories(
            project=project, user=request.user
        )

        serializer = GitHubRepositorySerializer(repositories, many=True)

        return Response({"repositories": serializer.data}, status=status.HTTP_200_OK)


class GitHubRepositoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organization_slug, project_slug, repository_id):
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

        repository = GitRepositoryService.get_repository(
            project=project, repository_id=repository_id
        )

        serializer = GitHubRepositorySerializer(repository)

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
