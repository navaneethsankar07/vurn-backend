from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CreateOrganizationSerializer
from .services.organization_service import OrganizationService
from .services.organization_options_service import OrganizationOptionsService
from .services.organization_query_service import OrganizationQueryService


class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = OrganizationQueryService.get_user_organizations(
            request.user,
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
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
