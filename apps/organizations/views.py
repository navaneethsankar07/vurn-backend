from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from apps.shared.utils.pagination import StandardPagination
from apps.shared.services.email_service import EmailService

from .constants import (
    ORGANIZATION_SORT_FIELDS,
    ORGANIZATION_SORT_ORDERS,
)

from .exceptions import (
    OrganizationNotFoundException,
    OrganizationAlreadyDeletedException,
    OrganizationAlreadyArchivedException,
    OrganizationPermissionDeniedException,
    InvalidOrganizationDeleteOTPException,
    OrganizationInvitationExpiredException,
    OrganizationInvitationNotFoundException,
    OrganizationMemberAlreadyExistsException,
    InvalidOrganizationRolePermissionsException,
    OrganizationInvitationAlreadyExistsException,
    OrganizationInvitationEmailMismatchException,
    OrganizationInvitationRecipientIsOwnerException,
    OrganizationInvitationPermissionDeniedException,
    OrganizationInvitationRecipientAlreadyMemberException,
)

from .serializers import (
    CreateOrganizationSerializer,
    OrganizationAccessSerializer,
    OrganizationDashboardSerializer,
    OrganizationDeleteConfirmSerializer,
    OrganizationDeleteRequestSerializer,
    OrganizationInvitationCreateSerializer,
    OrganizationListSerializer,
    OrganizationMemberListSerializer,
    OrganizationPreferenceSerializer,
    OrganizationRoleListSerializer,
    OrganizationRoleSerializer,
    ReceivedOrganizationInvitationSerializer,
    UpdateOrganizationBrandingSerializer,
    UpdateOrganizationSettingsSerializer,
)

from .services.organization_service import OrganizationService
from .services.organization_role_service import OrganizationRoleService
from .services.organization_query_service import OrganizationQueryService
from .services.organization_access_service import OrganizationAccessService
from .services.organization_member_service import OrganizationMemberService
from .services.organization_options_service import OrganizationOptionsService
from .services.organization_branding_service import OrganizationBrandingService
from .services.organization_deletion_service import OrganizationDeletionService
from .services.organization_dashboard_service import OrganizationDashboardService
from .services.organization_preference_service import OrganizationPreferenceService
from .services.organization_invitation_service import OrganizationInvitationService


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
            organization = OrganizationService.get_user_organization(
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


class OrganizationAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user,
                slug=slug,
            )

            access = OrganizationAccessService.get_user_access(
                organization=organization,
                user=request.user,
            )

        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationAccessSerializer(access)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class OrganizationRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        try:
            organization = OrganizationService.get_user_organization(
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


class OrganizationInvitationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user,
                slug=slug,
            )

            OrganizationAccessService.validate_member_invitation_access(
                organization=organization,
                user=request.user,
            )

        except OrganizationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except OrganizationInvitationPermissionDeniedException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrganizationInvitationCreateSerializer(
            data=request.data,
            context={
                "organization": organization,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            invitation = OrganizationInvitationService.create_invitation(
                organization=organization,
                invited_by=request.user,
                email=serializer.validated_data["email"],
                personal_message=(
                    serializer.validated_data.get(
                        "personal_message",
                        "",
                    )
                ),
                permission_role=(serializer.validated_data["permission_role"]),
                job_role_id=(serializer.validated_data["job_role_id"]),
            )

        except OrganizationInvitationAlreadyExistsException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except OrganizationInvitationRecipientAlreadyMemberException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except OrganizationInvitationRecipientIsOwnerException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation_url = f"{settings.FRONTEND_URL}" f"/invitations/{invitation.token}"

        send_email = serializer.validated_data.get(
            "send_email",
            False,
        )

        if send_email:
            EmailService.send_organization_invitation_email(
                recipient_email=invitation.email,
                organization_name=organization.name,
                invitation_link=invitation_url,
                personal_message=invitation.personal_message,
                expires_at=invitation.expires_at,
            )

        return Response(
            {
                "id": invitation.id,
                "email": invitation.email,
                "expires_at": invitation.expires_at,
                "invitation_url": invitation_url,
            },
            status=status.HTTP_201_CREATED,
        )


class ReceivedOrganizationInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invitations = OrganizationInvitationService.list_received_invitations(
            user=request.user,
        )

        serializer = ReceivedOrganizationInvitationSerializer(
            invitations,
            many=True,
        )

        return Response(serializer.data)


class OrganizationInvitationDetailView(APIView):

    def get(self, request, token):
        try:
            invitation = OrganizationInvitationService.get_invitation_by_token(
                token=token,
            )
        except OrganizationInvitationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except OrganizationInvitationExpiredException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_410_GONE,
            )

        return Response(
            {
                "organization": {
                    "name": invitation.organization.name,
                    "slug": invitation.organization.slug,
                    "icon": invitation.organization.icon,
                },
                "job_role": (
                    {
                        "id": invitation.job_role.id,
                        "name": invitation.job_role.name,
                    }
                    if invitation.job_role
                    else None
                ),
                "expires_at": invitation.expires_at,
            }
        )


class AcceptOrganizationInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        try:
            member = OrganizationInvitationService.accept_invitation(
                token=token,
                user=request.user,
            )
        except OrganizationInvitationNotFoundException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except OrganizationInvitationExpiredException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_410_GONE,
            )
        except OrganizationInvitationEmailMismatchException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except OrganizationMemberAlreadyExistsException as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": ("You have successfully joined the organization."),
                "organization_slug": member.organization.slug,
            },
            status=status.HTTP_200_OK,
        )


class OrganizationMemberView(APIView):

    permission_classes = [IsAuthenticated]

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
                permission_code="member.view",
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
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not OrganizationAccessService.has_permission(
            organization=organization,
            user=request.user,
            permission_code="member.view",
        ):
            return Response(
                {
                    "error": (
                        "You do not have permission " "to view organization members."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        search = request.query_params.get(
            "search",
        )

        role = request.query_params.get(
            "role",
            "all",
        )

        members = OrganizationMemberService.list_members(
            organization=organization,
            search=search,
            role=role,
        )

        paginator = StandardPagination()

        paginated_members = paginator.paginate_queryset(
            members,
            request,
        )

        serializer = OrganizationMemberListSerializer(
            paginated_members,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )
