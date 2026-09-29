import logging
import uuid

from django.db import transaction

from apps.shared.services.s3_service import S3Service

from ..models import Attachment
from ..constants import (
    ALLOWED_ATTACHMENT_MIME_TYPES,
    ATTACHMENT_UPLOAD_EXPIRY,
    MAX_ATTACHMENT_SIZE,
)
from ..exceptions import (
    AttachmentInvalidException,
    AttachmentNotFoundException,
    AttachmentUploadException,
    AttachmentUploadVerificationException,
)

logger = logging.getLogger("apps")


class AttachmentService:

    @staticmethod
    def _generate_object_key(*, issue, file_name):
        file_uuid = uuid.uuid4()

        return f"issues/{issue.id}/attachments/" f"{file_uuid}-{file_name}"

    @staticmethod
    def initialize_issue_upload(*, project, issue, file_name, file_size, mime_type):
        if issue.project_id != project.id:
            raise AttachmentInvalidException(
                "The issue does not belong to this project."
            )

        if issue.deleted_at is not None:
            raise AttachmentInvalidException("Cannot attach files to a deleted issue.")

        object_key = AttachmentService._generate_object_key(
            issue=issue, file_name=file_name
        )

        try:
            upload_url = S3Service.generate_upload_url(
                object_key=object_key,
                content_type=mime_type,
                expires_in=ATTACHMENT_UPLOAD_EXPIRY,
            )
        except Exception as exc:
            logger.exception(
                "Failed to generate attachment upload URL | issue=%s project=%s",
                issue.id,
                project.id,
            )
            raise AttachmentUploadException(
                "Unable to initialize attachment upload."
            ) from exc

        return {
            "upload_url": upload_url,
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "expires_in": ATTACHMENT_UPLOAD_EXPIRY,
            "object_key": object_key,
        }

    @staticmethod
    @transaction.atomic
    def complete_issue_upload(*, project, issue, user, object_key):
        if issue.project_id != project.id:
            raise AttachmentInvalidException(
                "The issue does not belong to this project."
            )

        if issue.deleted_at is not None:
            raise AttachmentInvalidException("Cannot attach files to a deleted issue.")

        prefix = f"issues/{issue.id}/attachments/"

        if not object_key.startswith(prefix):
            raise AttachmentInvalidException("Invalid attachment object.")

        try:
            metadata = S3Service.head_object(object_key=object_key)
        except Exception as exc:
            logger.exception(
                "Failed to verify attachment upload | " "issue=%s project=%s",
                issue.id,
                project.id,
            )
            raise AttachmentUploadVerificationException(
                "Unable to verify uploaded file."
            ) from exc

        file_size = metadata.get("ContentLength", 0)
        mime_type = metadata.get("ContentType", "").lower()

        if file_size < 1:
            raise AttachmentUploadVerificationException("Uploaded file is empty.")

        if file_size > MAX_ATTACHMENT_SIZE:
            raise AttachmentUploadVerificationException(
                "Uploaded file exceeds the 50 MB limit."
            )

        if mime_type not in ALLOWED_ATTACHMENT_MIME_TYPES:
            raise AttachmentUploadVerificationException(
                "Uploaded file type is not supported."
            )

        if Attachment.objects.filter(object_key=object_key).exists():
            raise AttachmentInvalidException(
                "This attachment has already been uploaded."
            )

        file_name = object_key.rsplit("/", 1)[-1]

        file_name = file_name.split("-", 1)[1]

        attachment = Attachment.objects.create(
            issue=issue,
            uploaded_by=user,
            file_name=file_name,
            object_key=object_key,
            file_size=file_size,
            mime_type=mime_type,
        )

        return attachment

    @staticmethod
    def list_issue_attachments(*, project, issue):
        if issue.project_id != project.id:
            raise AttachmentInvalidException(
                "The issue does not belong to this project."
            )

        if issue.deleted_at is not None:
            raise AttachmentInvalidException(
                "Cannot access attachments of a deleted issue."
            )

        return (
            Attachment.objects.filter(issue=issue)
            .select_related("uploaded_by")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def add_download_urls(*, attachments):
        for attachment in attachments:
            attachment.download_url = S3Service.generate_download_url(
                object_key=attachment.object_key
            )

        return attachments

    @staticmethod
    @transaction.atomic
    def delete_attachment(*, project, issue, attachment_id):
        if issue.project_id != project.id:
            raise AttachmentInvalidException(
                "The issue does not belong to this project."
            )

        if issue.deleted_at is not None:
            raise AttachmentInvalidException(
                "Cannot delete attachments of a deleted issue."
            )

        attachment = Attachment.objects.filter(id=attachment_id, issue=issue).first()

        if attachment is None:
            raise AttachmentNotFoundException("Attachment not found.")

        try:
            S3Service.delete_object(object_key=attachment.object_key)

            attachment.delete()
        except Exception as exc:
            logger.exception(
                "Failed to delete attachment | " "attachment=%s issue=%s project=%s",
                attachment.id,
                issue.id,
                project.id,
            )
            raise AttachmentUploadException("Unable to delete attachment.") from exc
