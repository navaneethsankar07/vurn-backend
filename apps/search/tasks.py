import logging

from celery import shared_task

from .services.indexing_service import SearchIndexingService

logger = logging.getLogger(__name__)


@shared_task(
    name="search.index_entity",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def index_search_entity(entity_type, entity_id):
    logger.info(
        "Starting search indexing | entity_type=%s entity_id=%s",
        entity_type,
        entity_id,
    )

    indexers = {
        "project": SearchIndexingService.index_project,
        "issue": SearchIndexingService.index_issue,
        "sprint": SearchIndexingService.index_sprint,
    }

    indexer = indexers.get(entity_type)

    if indexer is None:
        raise ValueError(f"Unsupported search entity type: {entity_type}")

    indexer(entity_id)

    logger.info(
        "Completed search indexing | entity_type=%s entity_id=%s",
        entity_type,
        entity_id,
    )
