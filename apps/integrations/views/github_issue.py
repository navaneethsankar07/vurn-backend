from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService

from ..exceptions import GitRepositoryException
from ..serializers import GitIssueQuerySerializer, GitIssueSerializer
from ..services.issue_service import GitIssueService


class GitHubIssueListView(APIView):
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

        ProjectAccessService.validate_project_view_access(
            project=project, user=request.user
        )

        query_serializer = GitIssueQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        data = query_serializer.validated_data

        try:
            repository, github_response = GitIssueService.get_repository_issues(
                project=project,
                repository_id=repository_id,
                state=data["state"],
                sort=data["sort"],
                direction=data["direction"],
                page=data["page"],
                per_page=data["page_size"],
            )

            issues = GitIssueService.sync_issues(
                repository=repository, github_issues=(github_response["issues"])
            )

        except GitRepositoryException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = GitIssueSerializer(issues, many=True)

        return Response(
            {
                "state": data["state"],
                "sort": data["sort"],
                "direction": data["direction"],
                "page": data["page"],
                "page_size": data["page_size"],
                "pagination": github_response["pagination"],
                "issues": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
