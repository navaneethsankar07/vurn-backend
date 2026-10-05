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
    def list_tags(*, project, search=None):
        tags = ProjectTag.objects.filter(project=project)

        if search:
            tags = tags.filter(name__icontains=search.strip())

        return tags.order_by("name", "id")

    @staticmethod
    @transaction.atomic
    def create_tag(*, project, name):
        if ProjectTag.objects.filter(project=project, name=name).exists():
            raise ProjectTagAlreadyExistsException(
                "A tag with this name already exists " "in this project."
            )

        try:
            return ProjectTag.objects.create(project=project, name=name)
        except IntegrityError as exc:
            logger.exception(
                "Failed to create project tag | " "project=%s name=%s", project.id, name
            )
            raise ProjectTagAlreadyExistsException(
                "Unable to create the document tag."
            ) from exc

    @staticmethod
    @transaction.atomic
    def add_tag(*, project, document, tag_id):
        tag = ProjectTag.objects.filter(id=tag_id, project=project).first()

        if tag is None:
            raise ProjectTagNotFoundException("Document tag not found.")

        if document.project_id != project.id:
            raise ProjectTagInvalidException(
                "The document does not belong to this project."
            )

        if DocumentTag.objects.filter(document=document, tag=tag).exists():
            raise ProjectTagAlreadyExistsException(
                "This tag is already attached to the document."
            )

        try:
            return DocumentTag.objects.create(document=document, tag=tag)
        except IntegrityError as exc:
            logger.exception(
                "Failed to add document tag | " "document=%s tag=%s",
                document.id,
                tag.id,
            )
            raise ProjectTagInvalidException("Unable to add the document tag.") from exc

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
