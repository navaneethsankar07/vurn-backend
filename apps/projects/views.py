from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.exceptions import (
    OrganizationNotFoundException,
)
from apps.organizations.services.organization_access_service import (
    OrganizationAccessService,
)
from apps.organizations.services.organization_service import (
    OrganizationService,
)

from .constants import PROJECT_ICONS
from .exceptions import (
    ProjectAlreadyExistsException,
    ProjectCreationPermissionDeniedException,
)
from .serializers import (
    ProjectCreateResponseSerializer,
    ProjectCreateSerializer,
)
from .services.project_service import ProjectService


class ProjectView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

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

        except ProjectCreationPermissionDeniedException as exc:
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

        response_serializer = ProjectCreateResponseSerializer(
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
