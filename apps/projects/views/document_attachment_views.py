from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    AttachmentInvalidException,
    AttachmentUploadException,
    AttachmentUploadVerificationException,
    DocumentNotFoundException,
    ProjectNotFoundException,
)
from ..serializers import AttachmentUploadSerializer, AttachmentUploadCompleteSerializer
from ..services.project_service import ProjectService
from ..services.document_service import DocumentService
from ..services.attachment_service import AttachmentService
from ..services.project_access_service import ProjectAccessService


class DocumentAttachmentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug, document_id):
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

        try:
            document = DocumentService.get_document(
                project=project, document_id=document_id
            )
        except DocumentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        ProjectAccessService.validate_knowledge_base_edit_access(
            project=project, user=request.user
        )

        serializer = AttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            upload = AttachmentService.initialize_upload(
                project=project, document=document, **serializer.validated_data
            )
        except AttachmentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except AttachmentUploadException as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": ("Attachment upload initialized successfully."),
                "upload_url": upload["upload_url"],
                "file_name": upload["file_name"],
                "file_size": upload["file_size"],
                "mime_type": upload["mime_type"],
                "expires_in": upload["expires_in"],
                "object_key": upload["object_key"],
            },
            status=status.HTTP_200_OK,
        )


class DocumentAttachmentUploadCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug, document_id):
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

        try:
            document = DocumentService.get_document(
                project=project, document_id=document_id
            )
        except DocumentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        ProjectAccessService.validate_knowledge_base_edit_access(
            project=project, user=request.user
        )

        serializer = AttachmentUploadCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = AttachmentService.complete_upload(
                project=project,
                document=document,
                user=request.user,
                **serializer.validated_data
            )
        except AttachmentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except AttachmentUploadVerificationException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Attachment uploaded successfully.",
                "attachment": {
                    "id": attachment.id,
                    "file_name": attachment.file_name,
                    "file_size": attachment.file_size,
                    "mime_type": attachment.mime_type,
                    "created_at": attachment.created_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )
