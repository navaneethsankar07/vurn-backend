from elasticsearch.helpers import bulk

from apps.projects.models import Issue, Project, Sprint
from apps.search.mappings import GLOBAL_SEARCH_INDEX
from apps.search.services.index_management_service import (
    SearchIndexManagementService,
)


class SearchIndexingService:
    @staticmethod
    def _project_document(project):
        return {
            "id": f"project-{project.pk}",
            "entity_type": "project",
            "entity_id": str(project.pk),
            "organization_id": str(project.organization_id),
            "project_id": str(project.pk),
            "project_key": project.key,
            "key": project.key,
            "slug": project.slug,
            "title": project.name,
            "description": project.description,
            "status": project.status,
            "is_archived": project.is_archived,
            "start_date": (
                project.start_date.isoformat() if project.start_date else None
            ),
            "target_date": (
                project.target_date.isoformat() if project.target_date else None
            ),
            "updated_at": project.updated_at.isoformat(),
        }

    @staticmethod
    def _issue_document(issue):
        project = issue.project

        return {
            "id": f"issue-{issue.pk}",
            "entity_type": "issue",
            "entity_id": str(issue.pk),
            "organization_id": str(project.organization_id),
            "project_id": str(project.pk),
            "project_key": project.key,
            "identifier": issue.key,
            "title": issue.title,
            "description": issue.description,
            "status": issue.status.name,
            "status_category": issue.status.category,
            "priority": issue.priority,
            "issue_type": issue.issue_type,
            "sprint_id": str(issue.sprint_id) if issue.sprint_id else None,
            "updated_at": issue.updated_at.isoformat(),
        }

    @staticmethod
    def _sprint_document(sprint):
        project = sprint.project

        return {
            "id": f"sprint-{sprint.pk}",
            "entity_type": "sprint",
            "entity_id": str(sprint.pk),
            "organization_id": str(project.organization_id),
            "project_id": str(project.pk),
            "project_key": project.key,
            "title": sprint.name,
            "description": sprint.description,
            "goal": sprint.goal,
            "status": sprint.status,
            "start_date": sprint.start_date.isoformat(),
            "end_date": sprint.end_date.isoformat(),
            "updated_at": sprint.updated_at.isoformat(),
        }

    @classmethod
    def _get_documents(cls):
        projects = Project.objects.filter(deleted_at__isnull=True)
        issues = Issue.objects.filter(
            deleted_at__isnull=True,
            project__deleted_at__isnull=True,
        ).select_related("project", "status")
        sprints = Sprint.objects.filter(
            project__deleted_at__isnull=True
        ).select_related("project")

        for project in projects.iterator():
            yield cls._project_document(project)

        for issue in issues.iterator():
            yield cls._issue_document(issue)

        for sprint in sprints.iterator():
            yield cls._sprint_document(sprint)

    @classmethod
    def reindex_all(cls):
        client = SearchIndexManagementService.get_client()

        if not client.indices.exists(index=GLOBAL_SEARCH_INDEX):
            SearchIndexManagementService.create_index()

        client.delete_by_query(
            index=GLOBAL_SEARCH_INDEX,
            query={"match_all": {}},
            refresh=True,
            conflicts="proceed",
        )

        actions = (
            {
                "_index": GLOBAL_SEARCH_INDEX,
                "_id": document["id"],
                "_source": document,
            }
            for document in cls._get_documents()
        )

        success_count, errors = bulk(
            client,
            actions,
            refresh=True,
            raise_on_error=False,
        )

        if errors:
            error_details = []

            for item in errors[:10]:
                operation, details = next(iter(item.items()))
                error_details.append(
                    {
                        "operation": operation,
                        "document_id": details.get("_id"),
                        "status": details.get("status"),
                        "error": details.get("error"),
                    }
                )

            raise RuntimeError(
                f"Search reindexing failed for {len(errors)} document(s). "
                f"Successfully indexed {success_count} document(s). "
                f"Sample errors: {error_details}"
            )

        return success_count
