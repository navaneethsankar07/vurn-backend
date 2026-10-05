import logging

from django.db import IntegrityError, transaction

from ..exceptions import ProjectTagAlreadyExistsException
from ..models import ProjectTag

logger = logging.getLogger(__name__)


class ProjectTagService:

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
