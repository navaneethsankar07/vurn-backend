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
from .exceptions import ProjectAlreadyExistsException, ProjectNotFoundException, ProjectPermissionDeniedException
from .serializers import (
    ProjectResponseSerializer,
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
)
from .services.project_service import ProjectService
from .services.project_access_service import ProjectAccessService


class ProjectView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        slug,
    ):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user,
                slug=slug,
            )

            OrganizationAccessService.validate_permission(
                organization=organization,
                user=request.user,
                permission_code="project.view",
            )

        except OrganizationNotFoundException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except OrganizationPermissionDeniedException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        search = request.query_params.get(
            "search",
        )

        project_status = request.query_params.get(
            "status",
            "all",
        )

        archive = request.query_params.get(
            "archive",
            "active",
        )

        sort = request.query_params.get(
            "sort",
            "recently_created",
        )

        projects = ProjectService.list_projects(
            organization=organization,
            search=search,
            status=project_status,
            archive=archive,
            sort=sort,
        )

        paginator = StandardPagination()

        paginated_projects = paginator.paginate_queryset(
            projects,
            request,
        )

        serializer = ProjectListSerializer(
            paginated_projects,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )

    def post(
        self,
        request,
        slug,
    ):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user,
                slug=slug,
            )

            OrganizationAccessService.validate_project_creation_access(
                organization=organization,
                user=request.user,
            )

        except OrganizationNotFoundException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except OrganizationProjectCreationPermissionDeniedException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            project = ProjectService.create_project(
                organization=organization,
                user=request.user,
                **serializer.validated_data,
            )

        except ProjectAlreadyExistsException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ProjectResponseSerializer(
            project,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ProjectOptionsView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
    ):
        return Response(
            {
                "icons": PROJECT_ICONS,
                "default_icon": "hexagon",
                "default_accent_color": "#F59E0B",
            }
        )


class ProjectSettingsView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def patch(
        self,
        request,
        slug,
        project_slug,
    ):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user,
                slug=slug,
            )

            project = ProjectService.get_project(
                organization=organization,
                slug=project_slug,
            )

            ProjectAccessService.validate_project_edit_access(
                project=project,
                user=request.user,
            )

        except OrganizationNotFoundException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except ProjectNotFoundException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except ProjectPermissionDeniedException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectUpdateSerializer(
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            project = ProjectService.update_project(
                project=project,
                **serializer.validated_data,
            )

        except ProjectAlreadyExistsException as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ProjectResponseSerializer(
            project,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
