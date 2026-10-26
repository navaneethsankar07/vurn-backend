from django.core.management.base import BaseCommand

from apps.search.services.index_management_service import (
    SearchIndexManagementService,
)


class Command(BaseCommand):
    help = "Create the Vurn global search index"

    def handle(self, *args, **options):
        created = SearchIndexManagementService.create_index()

        if created:
            self.stdout.write(
                self.style.SUCCESS("Global search index created successfully.")
            )
        else:
            self.stdout.write(self.style.WARNING("Global search index already exists."))
