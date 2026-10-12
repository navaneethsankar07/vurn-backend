from django.core.management.base import BaseCommand, CommandError

from apps.search.services.indexing_service import SearchIndexingService


class Command(BaseCommand):
    help = "Rebuild the Vurn global search index from PostgreSQL"

    def handle(self, *args, **options):
        try:
            count = SearchIndexingService.reindex_all()
        except Exception as exc:
            raise CommandError(f"Search reindexing failed: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {count} Vurn search documents.")
        )
