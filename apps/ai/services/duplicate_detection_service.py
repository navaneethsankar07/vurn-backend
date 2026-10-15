import json

from apps.ai.constants import DUPLICATE_ISSUE_DETECTION_PROMPT
from apps.ai.serializers import AIDuplicateDetectionResponseSerializer
from apps.ai.services.openrouter_service import OpenRouterService
from apps.projects.models import Issue
from apps.search.services.access_service import SearchAccessService
from apps.search.services.query_service import SearchQueryService


class DuplicateDetectionService:
    MAX_CANDIDATES = 10

    @classmethod
    def detect(
        cls,
        *,
        user,
        project_id,
        title,
        description="",
        issue_type="",
        priority="medium",
    ):
        allowed_project_ids = SearchAccessService.get_allowed_project_ids(user=user)

        accessible_issue_projects = {
            int(allowed_project_id)
            for allowed_project_id in allowed_project_ids.get("issue", [])
        }

        if project_id not in accessible_issue_projects:
            raise PermissionError(
                "You do not have permission to view issues in this project."
            )

        scoped_project_ids = {"project": [], "issue": [project_id], "sprint": []}

        query = f"{title} {description}".strip()

        search_result = SearchQueryService.search(
            query=query,
            allowed_project_ids=scoped_project_ids,
            page=1,
            page_size=cls.MAX_CANDIDATES,
        )

        search_candidates = [
            result
            for result in search_result["results"]
            if result.get("entity_type") == "issue"
        ]

        if not search_candidates:
            return {"duplicates": []}

        candidate_ids = [
            int(candidate["entity_id"])
            for candidate in search_candidates
            if str(candidate.get("entity_id", "")).isdigit()
        ]

        issues_by_id = {
            issue.id: issue
            for issue in Issue.objects.filter(
                id__in=candidate_ids, project_id=project_id, deleted_at__isnull=True
            ).select_related("project")
        }

        issues_by_key = {}
        candidates = []

        for result in search_candidates:
            entity_id = result.get("entity_id")

            if not str(entity_id).isdigit():
                continue

            issue = issues_by_id.get(int(entity_id))

            if issue is None:
                continue

            issues_by_key[issue.key] = issue

            candidates.append(
                {
                    "issue_key": issue.key,
                    "title": issue.title,
                    "description": (issue.description or "")[:2000],
                    "issue_type": issue.issue_type,
                    "priority": issue.priority,
                }
            )

        if not candidates:
            return {"duplicates": []}

        new_issue = {
            "title": title,
            "description": description,
            "issue_type": issue_type,
            "priority": priority,
        }

        ai_result = OpenRouterService.generate_json(
            messages=[
                {"role": "system", "content": DUPLICATE_ISSUE_DETECTION_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"new_issue": new_issue, "candidate_issues": candidates}
                    ),
                },
            ],
            serializer_class=AIDuplicateDetectionResponseSerializer,
            temperature=0.1,
            max_tokens=1200,
        )

        verified_duplicates = []

        for duplicate in ai_result["duplicates"]:
            issue_key = duplicate["issue_key"]
            issue = issues_by_key.get(issue_key)

            if issue is None:
                continue

            verified_duplicates.append(
                {
                    "issue_id": issue.id,
                    "key": issue.key,
                    "title": issue.title,
                    "reason": duplicate["reason"],
                    "confidence": duplicate["confidence"],
                }
            )
        return {"duplicates": verified_duplicates}
