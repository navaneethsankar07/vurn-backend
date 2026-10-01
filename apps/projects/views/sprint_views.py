from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    SprintInvalidException,
    SprintNotFoundException,
    ProjectNotFoundException,
    SprintCompletionException,
    SprintAlreadyExistsException,
    SprintCompletionBlockedException,
    ProjectPermissionDeniedException,
)

from ..serializers import (
    SprintSerializer,
    SprintCreateSerializer,
    SprintUpdateSerializer,
    SprintCompleteSerializer,
    SprintListQuerySerializer,
    SprintCompletionIssueSerializer,
)

from ..services.sprint_service import SprintService
from ..services.project_service import ProjectService
from ..services.project_access_service import ProjectAccessService


class SprintView(APIView):
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

        query_serializer = SprintListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        sprints = SprintService.list_sprints(
            project=project, **query_serializer.validated_data
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(sprints, request)

        serializer = SprintSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_sprint_creation_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = SprintCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            sprint = SprintService.create_sprint(
                project=project, user=request.user, **serializer.validated_data
            )
        except SprintAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SprintInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": sprint.id, "message": "Sprint created successfully."},
            status=status.HTTP_201_CREATED,
        )


class SprintDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, sprint_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            sprint = SprintService.get_sprint(project=project, sprint_id=sprint_id)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except SprintNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = SprintSerializer(sprint)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, slug, project_slug, sprint_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_sprint_management_access(
                project=project, user=request.user
            )

            sprint = SprintService.get_sprint(project=project, sprint_id=sprint_id)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except SprintNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = SprintUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            sprint = SprintService.update_sprint(
                sprint=sprint, **serializer.validated_data
            )
        except SprintAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SprintInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": sprint.id, "message": "Sprint updated successfully."},
            status=status.HTTP_200_OK,
        )


class SprintStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug, sprint_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_sprint_management_access(
                project=project, user=request.user
            )

            sprint = SprintService.get_sprint(project=project, sprint_id=sprint_id)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except SprintNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        try:
            sprint = SprintService.start_sprint(sprint=sprint)
        except SprintInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": sprint.id, "message": "Sprint started successfully."},
            status=status.HTTP_200_OK,
        )


class SprintCompletionCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, sprint_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            sprint = SprintService.get_sprint(project=project, sprint_id=sprint_id)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except SprintNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        completion_data = SprintService.get_sprint_completion_data(sprint=sprint)

        incomplete_issues = SprintCompletionIssueSerializer(
            completion_data["incomplete_issues"], many=True
        ).data

        incomplete_subtasks = SprintCompletionIssueSerializer(
            completion_data["incomplete_subtasks"], many=True
        ).data

        return Response(
            {
                "can_complete": completion_data["can_complete"],
                "requires_issue_action": bool(incomplete_issues),
                "requires_subtask_completion": bool(incomplete_subtasks),
                "incomplete_issues": incomplete_issues,
                "incomplete_subtasks": incomplete_subtasks,
            },
            status=status.HTTP_200_OK,
        )


class SprintCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug, sprint_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_sprint_management_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = SprintCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            sprint, target_sprint = SprintService.complete_sprint(
                project=project,
                sprint_id=sprint_id,
                user=request.user,
                **serializer.validated_data,
            )
        except SprintNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except SprintInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SprintCompletionBlockedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SprintCompletionException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": sprint.id,
                "status": sprint.status,
                "target_sprint_id": (target_sprint.id if target_sprint else None),
                "message": "Sprint completed successfully.",
            },
            status=status.HTTP_200_OK,
        )
