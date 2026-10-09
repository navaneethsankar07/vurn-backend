from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    IssueInvalidException,
    IssueNotFoundException,
    ProjectNotFoundException,
    IssueAlreadyExistsException,
    ProjectPermissionDeniedException,
)

from ..serializers import (
    IssueCreateSerializer,
    IssueUpdateSerializer,
    IssueResponseSerializer,
    IssueListQuerySerializer,
    WorkItemOptionSerializer,
    SubtaskListQuerySerializer,
    IssueSprintHistorySerializer,
)

from ..services.issue_service import IssueService
from ..services.project_service import ProjectService
from ..services.project_access_service import ProjectAccessService
from ..services.issue_sprint_history_service import IssueSprintHistoryService


class IssueView(APIView):

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

        query_serializer = IssueListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        try:
            issues = IssueService.list_issues(
                project=project, **query_serializer.validated_data
            )
        except IssueInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        paginator = StandardPagination()

        page = paginator.paginate_queryset(issues, request)

        response_serializer = IssueResponseSerializer(page, many=True)

        return paginator.get_paginated_response(response_serializer.data)

    def post(self, request, slug, project_slug):
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

        serializer = IssueCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            issue = IssueService.create_issue(
                project=project, user=request.user, **serializer.validated_data
            )
        except IssueInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except IssueAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = IssueResponseSerializer(issue)

        return Response(
            {
                "message": (f"{issue.issue_type} created successfully."),
                "issue": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class IssueDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, issue_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            issue = IssueService.get_issue(project=project, issue_id=issue_id)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = IssueResponseSerializer(issue)

        return Response(serializer.data, status=status.HTTP_200_OK)

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

        serializer = IssueUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            issue = IssueService.update_issue(
                project=project, issue_id=issue_id, **serializer.validated_data
            )
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except IssueInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = IssueResponseSerializer(issue)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_slug, issue_id):
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

        try:
            IssueService.delete_issue(project=project, issue_id=issue_id)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"message": "Issue deleted successfully."}, status=status.HTTP_200_OK
        )


class IssueSubtaskView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, issue_id):
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

        query_serializer = SubtaskListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        try:
            subtasks = IssueService.list_subtasks(
                project=project, issue_id=issue_id, **query_serializer.validated_data
            )
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        paginator = StandardPagination()

        page = paginator.paginate_queryset(subtasks, request)

        response_serializer = IssueResponseSerializer(page, many=True)

        return paginator.get_paginated_response(response_serializer.data)


class IssueSprintHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, issue_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_issue_view_access(
                project=project, user=request.user
            )

            issue = IssueService.get_issue(project=project, issue_id=issue_id)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        history = IssueSprintHistoryService.list_history(issue=issue)

        serializer = IssueSprintHistorySerializer(history, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkItemOptionListView(APIView):
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

        ProjectAccessService.validate_project_view_access(
            project=project, user=request.user
        )

        search = request.query_params.get("search")

        issues = IssueService.list_work_item_options(
            project=project, search=search or None
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(issues, request)
        serializer = WorkItemOptionSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
