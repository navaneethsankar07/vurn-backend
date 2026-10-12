GLOBAL_SEARCH_INDEX = "vurn-global-search-v1"

GLOBAL_SEARCH_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "id": {"type": "keyword"},
        "entity_type": {"type": "keyword"},
        "entity_id": {"type": "keyword"},
        "organization_id": {"type": "keyword"},
        "project_id": {"type": "keyword"},
        "project_key": {"type": "keyword"},
        "key": {"type": "keyword"},
        "slug": {"type": "keyword"},
        "identifier": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "title": {"type": "search_as_you_type", "max_shingle_size": 3},
        "description": {"type": "text"},
        "goal": {"type": "text"},
        "status": {"type": "keyword"},
        "priority": {"type": "keyword"},
        "issue_type": {"type": "keyword"},
        "status_category": {"type": "keyword"},
        "is_archived": {"type": "boolean"},
        "sprint_id": {"type": "keyword"},
        "start_date": {"type": "date"},
        "end_date": {"type": "date"},
        "target_date": {"type": "date"},
        "updated_at": {"type": "date"},
    },
}
