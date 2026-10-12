import logging

from django.db import transaction
from elasticsearch.helpers import bulk

from apps.projects.models import Issue, Project, Sprint
from ..mappings import GLOBAL_SEARCH_INDEX
from .index_management_service import SearchIndexManagementService

logger = logging.getLogger(__name__)


class SearchIndexingService:

    @staticmethod
    def _project_document(project):
        return {
            "id": f"project-{project.pk}",
            "entity_type": "project",
            "entity_id": str(project.pk),
            "organization_id": str(project.organization_id),
            "organization_slug": project.organization.slug,
            "project_id": str(project.pk),
            "project_slug": project.slug,
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
            "organization_slug": project.organization.slug,
            "project_id": str(project.pk),
            "project_slug": project.slug,
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
            "organization_slug": project.organization.slug,
            "project_id": str(project.pk),
            "project_slug": project.slug,
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
        projects = Project.objects.filter(deleted_at__isnull=True).select_related(
            "organization"
        )

        issues = Issue.objects.filter(
            deleted_at__isnull=True,
            project__deleted_at__isnull=True,
        ).select_related(
            "project",
            "project__organization",
            "status",
        )

        sprints = Sprint.objects.filter(
            project__deleted_at__isnull=True
        ).select_related(
            "project",
            "project__organization",
        )

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

    @classmethod
    def _save_document(cls, document):
        client = SearchIndexManagementService.get_client()

        client.index(
            index=GLOBAL_SEARCH_INDEX,
            id=document["id"],
            document=document,
        )

    @classmethod
    def _delete_document(cls, document_id):
        client = SearchIndexManagementService.get_client()

        client.options(ignore_status=404).delete(
            index=GLOBAL_SEARCH_INDEX,
            id=document_id,
        )

    @classmethod
    def index_project(cls, project_id):
        project = Project.objects.filter(
            pk=project_id,
            deleted_at__isnull=True,
        ).first()

        if project is None:
            cls.delete_project_documents(project_id)
            return

        cls._save_document(cls._project_document(project))

        for issue_id in (
            Issue.objects.filter(project_id=project_id)
            .values_list("pk", flat=True)
            .iterator()
        ):
            cls.index_issue(issue_id)

        for sprint_id in (
            Sprint.objects.filter(project_id=project_id)
            .values_list("pk", flat=True)
            .iterator()
        ):
            cls.index_sprint(sprint_id)

    @classmethod
    def index_issue(cls, issue_id):
        issue = (
            Issue.objects.filter(
                pk=issue_id,
                deleted_at__isnull=True,
                project__deleted_at__isnull=True,
            )
            .select_related(
                "project",
                "project__organization",
                "status",
            )
            .first()
        )

        if issue is None:
            cls._delete_document(f"issue-{issue_id}")
            return

        cls._save_document(cls._issue_document(issue))

    @classmethod
    def index_sprint(cls, sprint_id):
        sprint = (
            Sprint.objects.filter(
                pk=sprint_id,
                project__deleted_at__isnull=True,
            )
            .select_related(
                "project",
                "project__organization",
            )
            .first()
        )

        if sprint is None:
            cls._delete_document(f"sprint-{sprint_id}")
            return

        cls._save_document(cls._sprint_document(sprint))

    @classmethod
    def delete_project_documents(cls, project_id):
        client = SearchIndexManagementService.get_client()

        client.options(ignore_status=404).delete_by_query(
            index=GLOBAL_SEARCH_INDEX,
            query={"term": {"project_id": str(project_id)}},
            refresh=True,
            conflicts="proceed",
        )

    @classmethod
    def schedule_indexing(cls, entity_type, entity_id):
        supported_types = {"project", "issue", "sprint"}

        if entity_type not in supported_types:
            raise ValueError(f"Unsupported search entity type: {entity_type}")

        def enqueue_task():
            from apps.search.tasks import index_search_entity

            try:
                index_search_entity.delay(entity_type, entity_id)
            except Exception:
                logger.exception(
                    "Failed to enqueue search indexing task | "
                    "entity_type=%s entity_id=%s",
                    entity_type,
                    entity_id,
                )

        transaction.on_commit(enqueue_task)
