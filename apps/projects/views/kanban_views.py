from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    ProjectNotFoundException,
    KanbanIssueNotFoundException,
    KanbanIssuePositionException,
    KanbanStatusNotFoundException,
    KanbanInvalidMovementException,
)

from ..serializers import (
    KanbanIssueSerializer,
    KanbanIssueQuerySerializer,
    KanbanIssueStatusSerializer,
    KanbanSprintFilterSerializer,
    KanbanIssuePositionSerializer,
)

from ..services.kanban_service import KanbanService
from ..services.sprint_service import SprintService
from ..services.project_service import ProjectService


class KanbanBoardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        statuses = KanbanService.get_board(project=project)

        columns = [
            {
                "id": workflow_status.id,
                "name": workflow_status.name,
                "category": workflow_status.category,
                "color": workflow_status.color,
                "icon": workflow_status.icon,
                "position": workflow_status.position,
            }
            for workflow_status in statuses
        ]

        return Response({"columns": columns}, status=status.HTTP_200_OK)


class KanbanColumnIssueView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, status_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        query_serializer = KanbanIssueQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        try:
            workflow_status, issues = KanbanService.list_column_issues(
                project=project, status_id=status_id, **query_serializer.validated_data
            )
        except KanbanStatusNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        paginator = StandardPagination()

        page = paginator.paginate_queryset(issues, request)

        serializer = KanbanIssueSerializer(page, many=True)

        response = paginator.get_paginated_response(serializer.data)

        response.data["status"] = {
            "id": workflow_status.id,
            "name": workflow_status.name,
            "category": workflow_status.category,
        }

        return response


class KanbanSprintFilterView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        sprints = SprintService.list_project_sprints_for_board(project=project)

        serializer = KanbanSprintFilterSerializer(sprints, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class KanbanIssueStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, slug, project_slug, issue_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = KanbanIssueStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            issue = KanbanService.move_issue(
                project=project, issue_id=issue_id, **serializer.validated_data
            )
        except KanbanIssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except KanbanInvalidMovementException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": issue.id,
                "status_id": issue.status_id,
                "position": issue.position,
                "message": "Issue status updated successfully.",
            },
            status=status.HTTP_200_OK,
        )


class KanbanIssuePositionView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, slug, project_slug, issue_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = KanbanIssuePositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            issue = KanbanService.update_issue_position(
                project=project, issue_id=issue_id, **serializer.validated_data
            )
        except KanbanIssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except KanbanIssuePositionException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": issue.id,
                "status_id": issue.status_id,
                "position": issue.position,
                "message": "Issue position updated successfully.",
            },
            status=status.HTTP_200_OK,
        )
