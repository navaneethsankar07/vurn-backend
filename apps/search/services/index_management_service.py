from django.conf import settings
from elasticsearch import Elasticsearch

from apps.search.mappings import (
    GLOBAL_SEARCH_INDEX,
    GLOBAL_SEARCH_MAPPING,
)


class SearchIndexManagementService:
    @staticmethod
    def get_client():
        return Elasticsearch(settings.ELASTICSEARCH_URL)

    @classmethod
    def create_index(cls):
        client = cls.get_client()

        if client.indices.exists(index=GLOBAL_SEARCH_INDEX):
            return False

        client.indices.create(index=GLOBAL_SEARCH_INDEX, mappings=GLOBAL_SEARCH_MAPPING)

        return True
