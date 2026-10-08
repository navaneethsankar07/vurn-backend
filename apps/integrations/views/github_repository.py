from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService

from ..serializers.github_repository import GitHubRepositorySerializer
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
