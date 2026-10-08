from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService

from ..exceptions import GitRepositoryException
from ..serializers import GitPullRequestQuerySerializer, GitPullRequestSerializer
from ..services.pull_request_service import GitPullRequestService


class GitHubPullRequestListView(APIView):
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

        query_serializer = GitPullRequestQuerySerializer(data=request.query_params)

        query_serializer.is_valid(raise_exception=True)

        state = query_serializer.validated_data["state"]
        page = query_serializer.validated_data["page"]
        page_size = query_serializer.validated_data["page_size"]

        try:
            repository, github_response = (
                GitPullRequestService.get_repository_pull_requests(
                    project=project,
                    repository_id=repository_id,
                    state=state,
                    page=page,
                    per_page=page_size,
                )
            )

            pull_requests = GitPullRequestService.sync_pull_requests(
                repository=repository,
                github_pull_requests=(github_response["pull_requests"]),
            )

        except GitRepositoryException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = GitPullRequestSerializer(pull_requests, many=True)

        return Response(
            {
                "state": state,
                "page": page,
                "page_size": page_size,
                "pagination": (github_response["pagination"]),
                "pull_requests": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
