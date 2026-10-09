from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService
from apps.projects.services.project_service import ProjectService
from apps.organizations.services.organization_service import OrganizationService
from apps.shared.utils.pagination import StandardPagination

from ..serializers import (
    GitCommitSerializer,
    GitHubBranchSerializer,
    GitCommitQuerySerializer,
    GitHubRepositorySerializer,
    GitHubIntegrationStatusSerializer,
    GitHubRepositoryOverviewSerializer,
    GitHubRepositoryConnectionSerializer,
)

from ..exceptions import GitRepositoryAlreadyConnectedException, GitRepositoryException

from ..services.commit_service import GitCommitService
from ..services.branch_service import GitBranchService
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

        organization = OrganizationService.get_user_organization(
            user=request.user, slug=organization_slug
        )
        project = ProjectService.get_project(
            organization=organization, slug=project_slug
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


class GitHubCommitListView(APIView):
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

        query_serializer = GitCommitQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        branch = query_serializer.validated_data.get("branch")
        paginator = StandardPagination()

        page_number = request.query_params.get("page", 1)

        page_size = request.query_params.get("page_size", paginator.page_size)

        try:
            page_number = int(page_number)
            page_size = int(page_size)
        except ValueError:
            return Response(
                {"detail": ("Page and page_size must be valid integers.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if page_number < 1:
            return Response(
                {"detail": "Page must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if page_size < 1:
            return Response(
                {"detail": "Page size must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        page_size = min(page_size, 100)

        try:
            repository, github_response, resolved_branch = (
                GitCommitService.get_repository_commits(
                    project=project,
                    repository_id=repository_id,
                    branch=branch,
                    page=page_number,
                    per_page=page_size,
                )
            )

            commits = GitCommitService.sync_commits(
                repository=repository,
                github_commits=(github_response["commits"]),
                branch=resolved_branch,
            )

        except GitRepositoryException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = GitCommitSerializer(commits, many=True)

        return Response(
            {
                "branch": resolved_branch,
                "page": page_number,
                "page_size": page_size,
                "pagination": github_response["pagination"],
                "commits": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GitHubBranchListView(APIView):
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

        try:
            repository, branches = GitBranchService.get_repository_branches(
                project=project, repository_id=repository_id
            )
        except GitRepositoryException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = GitHubBranchSerializer(branches, many=True)

        return Response(
            {
                "repository_id": repository.id,
                "default_branch": repository.default_branch,
                "branches": serializer.data,
            },
            status=status.HTTP_200_OK,
        )