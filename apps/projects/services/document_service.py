import logging

from ..models import Document

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
