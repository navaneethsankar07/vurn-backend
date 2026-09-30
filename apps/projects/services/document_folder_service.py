import logging

from django.db import IntegrityError, transaction

from ..models import DocumentFolder
from ..exceptions import DocumentFolderAlreadyExistsException

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
