from django.template import context
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.constants import (
    ORGANIZATION_SORT_FIELDS,
    ORGANIZATION_SORT_ORDERS,
)

from .exceptions import (
    InvalidOrganizationDeleteOTPException,
    InvalidOrganizationRolePermissionsException,
    OrganizationAlreadyArchivedException,
    OrganizationAlreadyDeletedException,
    OrganizationNotFoundException,
    OrganizationRoleException,
)

from .serializers import (
    CreateOrganizationSerializer,
    OrganizationDashboardSerializer,
    OrganizationDeleteConfirmSerializer,
    OrganizationDeleteRequestSerializer,
    OrganizationListSerializer,
    OrganizationPreferenceSerializer,
    OrganizationRoleListSerializer,
    OrganizationRoleSerializer,
    UpdateOrganizationBrandingSerializer,
    UpdateOrganizationSettingsSerializer,
)

from .services.organization_service import OrganizationService
from .services.organization_role_service import OrganizationRoleService
from .services.organization_query_service import OrganizationQueryService
from .services.organization_options_service import OrganizationOptionsService
from .services.organization_branding_service import OrganizationBrandingService
from .services.organization_deletion_service import OrganizationDeletionService
from .services.organization_dashboard_service import OrganizationDashboardService
from .services.organization_preference_service import OrganizationPreferenceService


class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get(
            "search",
            "",
        ).strip()

        sort_by = request.query_params.get(
            "sort_by",
            "name",
        ).lower()

        order = request.query_params.get(
            "order",
            "asc",
        ).lower()

        if sort_by not in ORGANIZATION_SORT_FIELDS:
            return Response(
                {
                    "error": (
                        "Invalid sort_by. "
                        "Allowed values: name, member, "
                        "project, recent."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order not in ORGANIZATION_SORT_ORDERS:
            return Response(
                {
                    "error": ("Invalid order. " "Allowed values: asc, desc."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        organizations = OrganizationQueryService.get_user_organizations(
            user=request.user,
            search=search,
            sort_by=sort_by,
            order=order,
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(
            organizations,
            request,
            view=self,
        )

        serializer = OrganizationListSerializer(
            page,
            many=True,
        )

        response_data = {
            "recent": [],
            "pinned": [],
            "organizations": serializer.data,
        }

        return paginator.get_paginated_response(
            response_data,
        )

    def post(self, request):
        serializer = CreateOrganizationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        organization = OrganizationService.create_organization(
            owner=request.user,
            **serializer.validated_data,
        )

        return Response(
            {
                "message": "Organization created successfully.",
                "organization": {
                    "id": organization.id,
                    "name": organization.name,
                    "description": organization.description,
                    "slug": organization.slug,
                    "icon": organization.icon,
                    "accent_color": organization.accent_color,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class OrganizationOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        options = OrganizationOptionsService.get_options()

        return Response(
            options,
            status=status.HTTP_200_OK,
        )


class OrganizationDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        try:
            dashboard = OrganizationDashboardService.get_dashboard(
                user=request.user,
                slug=slug,
            )

            serializer = OrganizationDashboardSerializer(
                dashboard,
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )


class OrganizationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UpdateOrganizationSettingsSerializer(
            instance=organization,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        organization = OrganizationService.update_settings(
            organization=organization,
            validated_data=serializer.validated_data,
        )

        return Response(
            {
                "message": "Organization settings updated successfully.",
                "organization": {
                    "id": organization.id,
                    "name": organization.name,
                    "description": organization.description,
                    "slug": organization.slug,
                },
            },
            status=status.HTTP_200_OK,
        )


class OrganizationBrandingView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UpdateOrganizationBrandingSerializer(
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        organization = OrganizationBrandingService.update_branding(
            organization=organization,
            validated_data=serializer.validated_data,
        )

        return Response(
            {
                "message": "Organization branding updated successfully.",
                "organization": {
                    "id": organization.id,
                    "icon": organization.icon,
                    "accent_color": organization.accent_color,
                    "logo_url": organization.logo_url,
                },
            },
            status=status.HTTP_200_OK,
        )


class OrganizationArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )

            organization = OrganizationService.archive(
                organization=organization,
            )

        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except OrganizationAlreadyArchivedException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Organization archived successfully.",
            },
            status=status.HTTP_200_OK,
        )


class OrganizationDeleteRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationDeleteRequestSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        OrganizationDeletionService.request_deletion(
            user=request.user,
            organization=organization,
            name=serializer.validated_data["name"],
        )

        return Response(
            {
                "message": ("A verification code has been sent to your email."),
            },
            status=status.HTTP_200_OK,
        )


class OrganizationDeleteConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationDeleteConfirmSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            OrganizationDeletionService.confirm_deletion(
                user=request.user,
                organization=organization,
                otp=serializer.validated_data["otp"],
            )
        except OrganizationAlreadyDeletedException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidOrganizationDeleteOTPException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Organization deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class OrganizationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        preferences = OrganizationPreferenceService.get_preferences(
            organization=organization,
        )

        serializer = OrganizationPreferenceSerializer(preferences)

        return Response(serializer.data)

    def patch(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationPreferenceSerializer(
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        preferences = OrganizationPreferenceService.update_preferences(
            organization=organization,
            validated_data=serializer.validated_data,
        )

        return Response(
            OrganizationPreferenceSerializer(preferences).data,
            status=status.HTTP_200_OK,
        )


class OrganizationRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        search = request.query_params.get("search")
        sort = request.query_params.get("sort", "name")
        order = request.query_params.get("order", "asc")

        roles = OrganizationRoleService.list_roles(
            organization=organization,
            search=search,
            sort=sort,
            order=order,
        )

        paginator = StandardPagination()

        paginated_roles = paginator.paginate_queryset(
            roles,
            request,
        )

        serializer = OrganizationRoleListSerializer(
            paginated_roles,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )

    def post(self, request, slug):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationRoleSerializer(
            data=request.data,
            context={"organization": organization},
        )
        serializer.is_valid(raise_exception=True)

        try:
            role = OrganizationRoleService.create_role(
                organization=organization,
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
                color=serializer.validated_data.get("color", ""),
                permission_codes=serializer.validated_data.get("permissions", []),
            )
        except InvalidOrganizationRolePermissionsException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OrganizationRoleListSerializer(role).data,
            status=status.HTTP_201_CREATED,
        )


class OrganizationRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, slug, role_id):
        try:
            organization = OrganizationService.get_owned_organization(
                user=request.user,
                slug=slug,
            )
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationRoleSerializer(
            data=request.data,
            partial=True,
            context={
                "organization": organization,
                "role_id": role_id,
            },
        )

        serializer.is_valid(raise_exception=True)

        role = OrganizationRoleService.update_role(
            organization=organization,
            role_id=role_id,
            validated_data=serializer.validated_data,
        )

        return Response(
            OrganizationRoleListSerializer(role).data,
            status=status.HTTP_200_OK,
        )
