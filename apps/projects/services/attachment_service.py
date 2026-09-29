import logging
import uuid

from apps.shared.services.s3_service import S3Service
from ..constants import ATTACHMENT_UPLOAD_EXPIRY
from ..exceptions import (
    AttachmentInvalidException,
    AttachmentUploadException,
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
                "Failed to generate attachment upload URL | " "issue=%s project=%s",
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
