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
    ProjectAlreadyExistsException,
    ProjectDeleteConfirmationException,
    ProjectMemberAlreadyExistsException,
    ProjectMemberNotFoundException,
    ProjectMemberUserNotFoundException,
    ProjectNotFoundException,
    ProjectPermissionDeniedException,
    WorkflowStatusAlreadyExistsException,
    WorkflowStatusNotFoundException,
)
from .serializers import (
    ProjectDeleteSerializer,
    ProjectMemberCreateSerializer,
    ProjectMemberSerializer,
    ProjectResponseSerializer,
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectSettingsSerializer,
    ProjectUpdateSerializer,
    WorkflowOverviewSerializer,
    WorkflowStatusCreateSerializer,
    WorkflowStatusSerializer,
    WorkflowStatusUpdateSerializer,
)
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
