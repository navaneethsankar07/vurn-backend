from apps.search.mappings import GLOBAL_SEARCH_INDEX
from apps.search.services.index_management_service import (
    SearchIndexManagementService,
)


class SearchQueryService:
    SUGGESTION_LIMIT = 8
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 50

    ENTITY_TYPES = ("project", "issue", "sprint")

    @classmethod
    def _get_client(cls):
        return SearchIndexManagementService.get_client()

    @classmethod
    def _build_query(cls, query):
        query = query.strip()

        return {
            "bool": {
                "should": [
                    {
                        "term": {
                            "key": {
                                "value": query.upper(),
                                "boost": 10,
                            }
                        }
                    },
                    {
                        "term": {
                            "identifier.keyword": {
                                "value": query.upper(),
                                "boost": 10,
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": query,
                            "type": "bool_prefix",
                            "fields": [
                                "title",
                                "title._2gram",
                                "title._3gram",
                            ],
                            "boost": 5,
                        }
                    },
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["description", "goal"],
                            "type": "best_fields",
                            "boost": 1,
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        }

    @classmethod
    def _build_access_filter(cls, allowed_project_ids):
        access_filters = []

        for entity_type in cls.ENTITY_TYPES:
            project_ids = allowed_project_ids.get(entity_type, [])

            if not project_ids:
                continue

            access_filters.append(
                {
                    "bool": {
                        "filter": [
                            {"term": {"entity_type": entity_type}},
                            {
                                "terms": {
                                    "project_id": [
                                        str(project_id) for project_id in project_ids
                                    ]
                                }
                            },
                        ]
                    }
                }
            )

        if not access_filters:
            return None

        return {
            "bool": {
                "should": access_filters,
                "minimum_should_match": 1,
            }
        }

    @classmethod
    def _search(cls, query, allowed_project_ids, size, from_=0):
        if not query or not query.strip() or not allowed_project_ids:
            return {"total": 0, "results": []}

        access_filter = cls._build_access_filter(allowed_project_ids)

        if access_filter is None:
            return {"total": 0, "results": []}

        client = cls._get_client()

        response = client.search(
            index=GLOBAL_SEARCH_INDEX,
            query={
                "bool": {
                    "must": [cls._build_query(query)],
                    "filter": [access_filter],
                }
            },
            size=size,
            from_=from_,
        )

        total = response["hits"]["total"]
        total = total["value"] if isinstance(total, dict) else total

        return {
            "total": total,
            "results": [
                {
                    "id": hit["_source"]["id"],
                    "entity_type": hit["_source"]["entity_type"],
                    "entity_id": hit["_source"]["entity_id"],
                    "project_id": hit["_source"]["project_id"],
                    "project_key": hit["_source"].get("project_key"),
                    "key": hit["_source"].get("key"),
                    "identifier": hit["_source"].get("identifier"),
                    "title": hit["_source"]["title"],
                    "description": hit["_source"].get("description", ""),
                    "status": hit["_source"].get("status"),
                    "priority": hit["_source"].get("priority"),
                    "issue_type": hit["_source"].get("issue_type"),
                    "updated_at": hit["_source"].get("updated_at"),
                }
                for hit in response["hits"]["hits"]
            ],
        }

    @classmethod
    def get_suggestions(cls, query, allowed_project_ids):
        return cls._search(
            query=query,
            allowed_project_ids=allowed_project_ids,
            size=cls.SUGGESTION_LIMIT,
        )

    @classmethod
    def search(
        cls,
        query,
        allowed_project_ids,
        page=1,
        page_size=DEFAULT_PAGE_SIZE,
    ):
        page = max(1, int(page))
        page_size = min(
            cls.MAX_PAGE_SIZE,
            max(1, int(page_size)),
        )

        return cls._search(
            query=query,
            allowed_project_ids=allowed_project_ids,
            size=page_size,
            from_=(page - 1) * page_size,
        )
