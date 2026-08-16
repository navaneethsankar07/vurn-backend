from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.constants import (
    ORGANIZATION_SORT_FIELDS,
    ORGANIZATION_SORT_ORDERS,
)
from .exceptions import OrganizationNotFoundException

from .serializers import (
    CreateOrganizationSerializer,
    OrganizationDashboardSerializer,
    OrganizationListSerializer,
    UpdateOrganizationBrandingSerializer,
    UpdateOrganizationSettingsSerializer,
)

from .services.organization_service import OrganizationService
from .services.organization_query_service import OrganizationQueryService
from .services.organization_options_service import OrganizationOptionsService
from .services.organization_branding_service import OrganizationBrandingService
from .services.organization_dashboard_service import OrganizationDashboardService


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
        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        organization = OrganizationService.archive(
            organization=organization,
        )

        return Response(
            {
                "message": "Organization archived successfully.",
            },
            status=status.HTTP_200_OK,
        )
