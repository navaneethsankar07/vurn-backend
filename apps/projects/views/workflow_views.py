from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    ProjectNotFoundException,
    WorkflowStatusNotFoundException,
    ProjectPermissionDeniedException,
    WorkflowTransitionStatusException,
    WorkflowTransitionInvalidException,
    WorkflowTransitionNotFoundException,
    WorkflowStatusAlreadyExistsException,
    WorkflowStatusCannotBeDeletedException,
    WorkflowTransitionAlreadyExistsException,
)

from ..serializers import (
    WorkflowStatusSerializer,
    WorkflowOverviewSerializer,
    WorkflowStatusUpdateSerializer,
    WorkflowStatusCreateSerializer,
    WorkflowStatusPositionSerializer,
    WorkflowTransitionCreateSerializer,
    WorkflowTransitionUpdateSerializer,
)

from ..services.project_service import ProjectService
from ..services.workflow_service import WorkflowService
from ..services.project_access_service import ProjectAccessService


class ProjectWorkflowView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            workflow = WorkflowService.get_workflow(project=project)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = WorkflowOverviewSerializer(workflow)

        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkflowStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_workflow_management_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkflowStatusCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            workflow_status = WorkflowService.create_status(
                project=project, **serializer.validated_data
            )
        except WorkflowStatusAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = WorkflowStatusSerializer(workflow_status)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, slug, project_slug, status_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_workflow_management_access(
                project=project, user=request.user
            )

            workflow_status = WorkflowService.get_status(
                project=project, status_id=status_id
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except WorkflowStatusNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkflowStatusUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            workflow_status = WorkflowService.update_status(
                status=workflow_status, **serializer.validated_data
            )
        except WorkflowStatusAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = WorkflowStatusSerializer(workflow_status)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_slug, status_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_workflow_management_access(
                project=project, user=request.user
            )

            workflow_status = WorkflowService.get_status(
                project=project, status_id=status_id
            )

            WorkflowService.delete_status(status=workflow_status)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except WorkflowStatusNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except WorkflowStatusCannotBeDeletedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Workflow status deleted successfully."},
            status=status.HTTP_200_OK,
        )


class WorkflowTransitionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_workflow_management_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkflowTransitionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            WorkflowService.create_transition(
                project=project, **serializer.validated_data
            )
        except WorkflowTransitionInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except WorkflowTransitionStatusException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except WorkflowTransitionAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Workflow transition created successfully."},
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request, slug, project_slug, transition_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_workflow_management_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkflowTransitionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            WorkflowService.update_transition(
                project=project,
                transition_id=transition_id,
                **serializer.validated_data,
            )
        except WorkflowTransitionNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except WorkflowTransitionInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except WorkflowTransitionStatusException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except WorkflowTransitionAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Workflow transition updated successfully."},
            status=status.HTTP_200_OK,
        )


class WorkflowStatusPositionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, slug, project_slug, status_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_workflow_management_access(
                project=project, user=request.user
            )

            workflow_status = WorkflowService.get_status(
                project=project, status_id=status_id
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except WorkflowStatusNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkflowStatusPositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow_status = WorkflowService.update_status_position(
            status=workflow_status, **serializer.validated_data
        )

        response_serializer = WorkflowStatusSerializer(workflow_status)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
