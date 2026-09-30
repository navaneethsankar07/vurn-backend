from apps.projects.models import DocumentFolder


class DocumentFolderService:

    @staticmethod
    def list_folders(*, project, search=None):
        folders = DocumentFolder.objects.filter(project=project).select_related(
            "created_by"
        )

        if search:
            folders = folders.filter(name__icontains=search.strip())

        return folders.order_by("name", "id")
