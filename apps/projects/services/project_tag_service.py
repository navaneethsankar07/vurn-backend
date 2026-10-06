import logging

from django.db import IntegrityError, transaction

from ..exceptions import (
    ProjectTagAlreadyExistsException,
    ProjectTagInvalidException,
    ProjectTagNotFoundException,
)
from ..models import DocumentTag, ProjectTag

logger = logging.getLogger(__name__)


class ProjectTagService:

    @staticmethod
    def list_document_tags(*, project, document, search=None):
        tags = ProjectTag.objects.filter(project=project, documents=document)

        if search:
            tags = tags.filter(name__icontains=search.strip())

        return tags.order_by("name", "id")

    @staticmethod
    @transaction.atomic
    def create_tag(*, project, document, name):
        tag = ProjectTag.objects.filter(project=project, name=name).first()

        if tag is None:
            try:
                tag = ProjectTag.objects.create(project=project, name=name)
            except IntegrityError as exc:
                logger.exception(
                    "Failed to create project tag | " "project=%s name=%s",
                    project.id,
                    name,
                )
                raise ProjectTagAlreadyExistsException(
                    "Unable to create the document tag."
                ) from exc

        if DocumentTag.objects.filter(document=document, tag=tag).exists():
            raise ProjectTagAlreadyExistsException(
                "This tag is already attached to the document."
            )

        try:
            DocumentTag.objects.create(document=document, tag=tag)
        except IntegrityError as exc:
            logger.exception(
                "Failed to attach document tag | " "document=%s tag=%s",
                document.id,
                tag.id,
            )
            raise ProjectTagInvalidException("Unable to add the document tag.") from exc

        return tag

    @staticmethod
    @transaction.atomic
    def remove_tag(*, project, document, tag_id):
        tag = ProjectTag.objects.filter(id=tag_id, project=project).first()

        if tag is None:
            raise ProjectTagNotFoundException("Document tag not found.")

        document_tag = DocumentTag.objects.filter(document=document, tag=tag).first()

        if document_tag is None:
            raise ProjectTagNotFoundException(
                "This tag is not attached to the document."
            )

        document_tag.delete()
