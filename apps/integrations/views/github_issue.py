from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.services.project_access_service import ProjectAccessService
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService
from apps.projects.exceptions import ProjectNotFoundException
from apps.projects.services.project_service import ProjectService


from ..exceptions import (
    GitIssueAlreadyLinkedException,
    GitIssueAutoMatchException,
    GitIssueClosedException,
    GitIssueLinkLimitException,
    GitRepositoryException,
)
from ..serializers import (
    GitIssueSerializer,
    GitIssueLinkSerializer,
    GitIssueQuerySerializer,
    GitIssueWorkItemSerializer,
)
from ..services.issue_service import GitIssueService
from ..services.git_issue_link_service import GitIssueLinkService


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


class GitIssueLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(
        self, request, organization_slug, project_slug, repository_id, git_issue_id
    ):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=organization_slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        ProjectAccessService.validate_project_edit_access(
            project=project, user=request.user
        )

        serializer = GitIssueLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            link, matched_by = GitIssueLinkService.link_work_item(
                project=project,
                repository_id=repository_id,
                git_issue_id=git_issue_id,
                issue_id=serializer.validated_data.get("issue_id"),
                auto_match=serializer.validated_data.get("auto_match", False),
            )
        except GitIssueClosedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except GitIssueAlreadyLinkedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        except GitIssueAutoMatchException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except GitRepositoryException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except GitIssueLinkLimitException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(
            {
                "message": "GitHub issue linked successfully.",
                "matched_by": matched_by,
                "link": GitIssueWorkItemSerializer(link).data,
            },
            status=status.HTTP_201_CREATED,
        )
