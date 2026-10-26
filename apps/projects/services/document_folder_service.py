import logging

from django.db import IntegrityError, transaction

from ..models import DocumentFolder
from ..exceptions import (
    DocumentFolderAlreadyExistsException,
    DocumentFolderInvalidException,
    DocumentFolderNotFoundException,
)

logger = logging.getLogger(__name__)


class DocumentFolderService:

    @staticmethod
    def list_folders(*, project, search=None):
        folders = DocumentFolder.objects.filter(project=project).select_related(
            "created_by"
        )

        if search:
            folders = folders.filter(name__icontains=search.strip())

        return folders.order_by("name", "id")

    @staticmethod
    @transaction.atomic
    def create_folder(*, project, user, name):
        if DocumentFolder.objects.filter(project=project, name=name).exists():
            raise DocumentFolderAlreadyExistsException(
                "A folder with this name already exists " "in this project."
            )

        try:
            return DocumentFolder.objects.create(
                project=project, name=name, created_by=user
            )
        except IntegrityError as exc:
            logger.exception(
                "Failed to create document folder | " "project=%s name=%s user=%s",
                project.id,
                name,
                user.id,
            )
            raise DocumentFolderAlreadyExistsException(
                "Unable to create the document folder."
            ) from exc

    @staticmethod
    @transaction.atomic
    def update_folder(*, project, folder_id, name):
        folder = (
            DocumentFolder.objects.select_for_update()
            .filter(id=folder_id, project=project)
            .first()
        )

        if folder is None:
            raise DocumentFolderNotFoundException("Document folder not found.")

        if (
            DocumentFolder.objects.filter(project=project, name=name)
            .exclude(id=folder.id)
            .exists()
        ):
            raise DocumentFolderAlreadyExistsException(
                "A folder with this name already exists " "in this project."
            )

        try:
            folder.name = name
            folder.save(update_fields=["name", "updated_at"])
        except IntegrityError as exc:
            logger.exception(
                "Failed to update document folder | " "folder=%s project=%s",
                folder.id,
                project.id,
            )
            raise DocumentFolderAlreadyExistsException(
                "Unable to update the document folder."
            ) from exc

        return folder

    @staticmethod
    @transaction.atomic
    def delete_folder(*, project, folder_id):
        folder = (
            DocumentFolder.objects.select_for_update()
            .filter(id=folder_id, project=project)
            .first()
        )

        if folder is None:
            raise DocumentFolderNotFoundException("Document folder not found.")

        if folder.documents.filter(deleted_at__isnull=True).exists():
            raise DocumentFolderInvalidException(
                "Cannot delete a folder that contains documents."
            )

        try:
            folder.documents.filter(deleted_at__isnull=True).delete()

            folder.documents.filter(deleted_at__isnull=False).delete()

            folder.delete()
        except Exception:
            logger.exception(
                "Failed to delete document folder | " "folder=%s project=%s",
                folder.id,
                project.id,
            )
            raise
