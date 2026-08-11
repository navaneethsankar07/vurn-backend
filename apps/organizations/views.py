from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.serializers import (
    CreateOrganizationSerializer,
)
from apps.organizations.services.organization_service import (
    OrganizationService,
)


class CreateOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

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
