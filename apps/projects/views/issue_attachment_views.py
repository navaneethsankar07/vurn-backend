from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    IssueNotFoundException,
    ProjectNotFoundException,
    AttachmentUploadException,
    AttachmentInvalidException,
    AttachmentNotFoundException,
    AttachmentUploadVerificationException,
)

from ..serializers import (
    AttachmentSerializer,
    AttachmentUploadSerializer,
    AttachmentUploadCompleteSerializer,
)

from ..services.issue_service import IssueService
from ..services.project_service import ProjectService
from ..services.attachment_service import AttachmentService


class IssueAttachmentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug, issue_id):
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

        serializer = AttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            issue = IssueService.get_issue(project=project, issue_id=issue_id)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        try:
            upload = AttachmentService.initialize_issue_upload(
                project=project, issue=issue, **serializer.validated_data
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


class IssueAttachmentUploadCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug, issue_id):
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

        serializer = AttachmentUploadCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            issue = IssueService.get_issue(project=project, issue_id=issue_id)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        try:
            attachment = AttachmentService.complete_issue_upload(
                project=project,
                issue=issue,
                user=request.user,
                **serializer.validated_data,
            )
        except AttachmentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except AttachmentUploadVerificationException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": ("Attachment uploaded successfully."),
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


class IssueAttachmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, issue_id):
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
            issue = IssueService.get_issue(project=project, issue_id=issue_id)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        try:
            attachments = AttachmentService.list_issue_attachments(
                project=project, issue=issue
            )
        except AttachmentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        paginator = StandardPagination()

        page = paginator.paginate_queryset(attachments, request)

        AttachmentService.add_download_urls(attachments=page)

        serializer = AttachmentSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class IssueAttachmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, slug, project_slug, issue_id, attachment_id):
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
            issue = IssueService.get_issue(project=project, issue_id=issue_id)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        try:
            AttachmentService.delete_attachment(
                project=project, issue=issue, attachment_id=attachment_id
            )
        except AttachmentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except AttachmentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except AttachmentUploadException as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "Attachment deleted successfully."}, status=status.HTTP_200_OK
        )
