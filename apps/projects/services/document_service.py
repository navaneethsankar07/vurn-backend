import logging

from django.db import IntegrityError, transaction

from ..exceptions import DocumentInvalidException, DocumentNotFoundException

from ..models import Document, DocumentFolder

logger = logging.getLogger(__name__)


class DocumentService:

    @staticmethod
    def list_documents(*, project, folder_id=None, search=None, sort="updated_desc"):
        documents = Document.objects.filter(
            project=project, deleted_at__isnull=True
        ).select_related("folder", "created_by")

        if folder_id is not None:
            documents = documents.filter(folder_id=folder_id)

        if search:
            documents = documents.filter(title__icontains=search.strip())

        ordering = {
            "updated_desc": "-updated_at",
            "updated_asc": "updated_at",
            "created_desc": "-created_at",
            "created_asc": "created_at",
            "title_asc": "title",
            "title_desc": "-title",
        }

        return documents.order_by(ordering.get(sort, "-updated_at"), "id")

    @staticmethod
    @transaction.atomic
    def create_document(*, project, user, folder_id, title, content):
        folder = DocumentFolder.objects.filter(id=folder_id, project=project).first()

        if folder is None:
            raise DocumentInvalidException(
                "The document folder does not belong " "to this project."
            )

        try:
            return Document.objects.create(
                project=project,
                folder=folder,
                title=title,
                content=content,
                created_by=user,
            )
        except IntegrityError as exc:
            logger.exception(
                "Failed to create document | " "project=%s folder=%s user=%s",
                project.id,
                folder.id,
                user.id,
            )
            raise DocumentInvalidException("Unable to create the document.") from exc

    @staticmethod
    def get_document(*, project, document_id):
        document = (
            Document.objects.filter(
                project=project, id=document_id, deleted_at__isnull=True
            )
            .select_related("folder", "created_by")
            .first()
        )

        if document is None:
            raise DocumentNotFoundException("Document not found.")

        return document

    @staticmethod
    @transaction.atomic
    def update_document(*, project, document_id, **validated_data):
        document = DocumentService.get_document(
            project=project, document_id=document_id
        )

        if "folder_id" in validated_data:
            folder_id = validated_data.pop("folder_id")

            folder = DocumentFolder.objects.filter(
                id=folder_id, project=project
            ).first()

            if folder is None:
                raise DocumentInvalidException(
                    "The document folder does not belong " "to this project."
                )

            document.folder = folder

        for field, value in validated_data.items():
            setattr(document, field, value)

        try:
            document.save()
        except IntegrityError as exc:
            logger.exception(
                "Failed to update document | " "document=%s project=%s",
                document.id,
                project.id,
            )
            raise DocumentInvalidException("Unable to update the document.") from exc

        return document
