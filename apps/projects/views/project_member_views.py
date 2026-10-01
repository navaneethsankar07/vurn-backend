from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.organizations.exceptions import OrganizationNotFoundException
from apps.shared.utils.pagination import StandardPagination
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    ProjectNotFoundException,
    ProjectMemberNotFoundException,
    ProjectPermissionDeniedException,
    ProjectMemberUserNotFoundException,
    ProjectMemberAlreadyExistsException,
)

from ..serializers import (
    ProjectMemberSerializer,
    ProjectMemberCreateSerializer,
)

from ..services.project_service import ProjectService
from ..services.project_access_service import ProjectAccessService
from ..services.project_member_service import ProjectMemberService


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
