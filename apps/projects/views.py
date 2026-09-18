from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.organizations.exceptions import (
    OrganizationNotFoundException,
    OrganizationPermissionDeniedException,
    OrganizationProjectCreationPermissionDeniedException,
)
from apps.organizations.services.organization_access_service import (
    OrganizationAccessService,
)
from apps.organizations.services.organization_service import (
    OrganizationService,
)
from apps.shared.utils.pagination import StandardPagination

from .constants import PROJECT_ICONS
from .exceptions import (
    KanbanInvalidMovementException,
    KanbanIssueNotFoundException,
    ProjectAlreadyExistsException,
    ProjectDeleteConfirmationException,
    ProjectMemberAlreadyExistsException,
    ProjectMemberNotFoundException,
    ProjectMemberUserNotFoundException,
    ProjectNotFoundException,
    ProjectPermissionDeniedException,
    SprintAlreadyExistsException,
    SprintInvalidException,
    SprintNotFoundException,
    WorkflowStatusAlreadyExistsException,
    WorkflowStatusCannotBeDeletedException,
    WorkflowStatusNotFoundException,
    WorkflowTransitionAlreadyExistsException,
    WorkflowTransitionInvalidException,
    WorkflowTransitionNotFoundException,
    WorkflowTransitionStatusException,
)
from .serializers import (
    KanbanIssuePositionSerializer,
    KanbanIssueQuerySerializer,
    KanbanIssueSerializer,
    KanbanIssueStatusSerializer,
    KanbanSprintFilterSerializer,
    ProjectDeleteSerializer,
    ProjectMemberCreateSerializer,
    ProjectMemberSerializer,
    ProjectResponseSerializer,
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectSettingsSerializer,
    ProjectUpdateSerializer,
    SprintCreateSerializer,
    SprintListQuerySerializer,
    SprintSerializer,
    SprintUpdateSerializer,
    WorkflowOverviewSerializer,
    WorkflowStatusCreateSerializer,
    WorkflowStatusPositionSerializer,
    WorkflowStatusSerializer,
    WorkflowStatusUpdateSerializer,
    WorkflowTransitionCreateSerializer,
    WorkflowTransitionSerializer,
    WorkflowTransitionUpdateSerializer,
)
from .services.sprint_service import SprintService
from .services.kanban_service import KanbanService
from .services.project_service import ProjectService
from .services.workflow_service import WorkflowService
from .services.project_access_service import ProjectAccessService
from .services.project_member_service import ProjectMemberService


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            OrganizationAccessService.validate_permission(
                organization=organization,
                user=request.user,
                permission_code="project.view",
            )

        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        except OrganizationPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        search = request.query_params.get("search")

        project_status = request.query_params.get("status", "all")

        archive = request.query_params.get("archive", "active")

        sort = request.query_params.get("sort", "recently_created")

        projects = ProjectService.list_projects(
            organization=organization,
            search=search,
            status=project_status,
            archive=archive,
            sort=sort,
        )

        paginator = StandardPagination()

        paginated_projects = paginator.paginate_queryset(projects, request)

        serializer = ProjectListSerializer(paginated_projects, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            OrganizationAccessService.validate_project_creation_access(
                organization=organization, user=request.user
            )

        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        except OrganizationProjectCreationPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            project = ProjectService.create_project(
                organization=organization,
                user=request.user,
                **serializer.validated_data,
            )

        except ProjectAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = ProjectResponseSerializer(
            project,
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ProjectOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "icons": PROJECT_ICONS,
                "default_icon": "hexagon",
                "default_accent_color": "#F59E0B",
            }
        )


class ProjectSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            ProjectAccessService.validate_project_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        response_serializer = ProjectSettingsSerializer(project)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_project_edit_access(
                project=project, user=request.user
            )

        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectUpdateSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        try:
            project = ProjectService.update_project(
                project=project, **serializer.validated_data
            )

        except ProjectAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = ProjectResponseSerializer(project)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ProjectArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            ProjectAccessService.validate_project_archive_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        project = ProjectService.set_project_archive_status(
            project=project, is_archived=True
        )

        response_serializer = ProjectResponseSerializer(project)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ProjectUnarchiveView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_project_archive_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        project = ProjectService.set_project_archive_status(
            project=project, is_archived=False
        )

        response_serializer = ProjectResponseSerializer(project)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ProjectDeleteView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def delete(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            ProjectAccessService.validate_project_delete_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ProjectService.validate_delete_confirmation(
                project=project, confirmation=serializer.validated_data["confirmation"]
            )
        except ProjectDeleteConfirmationException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        ProjectService.delete_project(project=project)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            ProjectAccessService.validate_project_view_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        search = request.query_params.get("search")
        sort = request.query_params.get("sort", "recently_added")

        members = ProjectMemberService.list_members(
            project=project, search=search, sort=sort
        )

        paginator = StandardPagination()

        paginated_members = paginator.paginate_queryset(members, request)

        serializer = ProjectMemberSerializer(paginated_members, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            ProjectAccessService.validate_add_project_member_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ProjectMemberService.add_member(
                project=project, **serializer.validated_data
            )
        except ProjectMemberUserNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectMemberAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Project member added successfully."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, slug, project_slug, user_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            ProjectAccessService.validate_remove_project_member_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        try:
            ProjectMemberService.remove_member(project=project, user_id=user_id)
        except ProjectMemberNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "message": "Project member removed successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ProjectWorkflowView(APIView):

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


class SprintView(APIView):

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


class KanbanBoardView(APIView):

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
                "hello": "hai",
            }
            for workflow_status in statuses
        ]

        return Response({"columns": columns}, status=status.HTTP_200_OK)


class KanbanColumnIssueView(APIView):

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
        except KanbanInvalidMovementException as exc:
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
                "id": issue["id"],
                "status_id": issue["status_id"],
                "position": issue["position"],
                "message": ("Issue status updated successfully."),
            },
            status=status.HTTP_200_OK,
        )


class KanbanIssuePositionView(APIView):

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

        return Response(
            {
                "id": issue["id"],
                "status_id": issue["status_id"],
                "position": issue["position"],
                "message": ("Issue position updated successfully."),
            },
            status=status.HTTP_200_OK,
        )
