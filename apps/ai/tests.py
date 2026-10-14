from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import httpx
from django.test import SimpleTestCase, override_settings
from rest_framework import serializers, status
from rest_framework.test import APIRequestFactory, force_authenticate


from apps.ai.exceptions import (
    AIConfigurationError,
    AIProviderTimeoutError,
    AIStructuredOutputError,
)
from .services.sprint_summary_service import SprintSummaryService

from .views import TaskBreakdownView

from .services.duplicate_detection_service import DuplicateDetectionService
from .services.story_point_estimation_service import StoryPointEstimationService
from .services.openrouter_service import OpenRouterService
from .services.task_breakdown_service import TaskBreakdownService


class ExampleOutputSerializer(serializers.Serializer):
    title = serializers.CharField()
    items = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )


@override_settings(
    OPENROUTER_API_KEY="test-key",
    OPENROUTER_MODEL="test/model",
    OPENROUTER_BASE_URL="https://openrouter.ai/api/v1",
    OPENROUTER_TIMEOUT=10,
    OPENROUTER_MAX_TOKENS=100,
)
class OpenRouterServiceTests(SimpleTestCase):
    @patch("apps.ai.services.openrouter_service.httpx.post")
    def test_generate_returns_content(self, mock_post):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated response"}}]
        }
        mock_post.return_value = mock_response

        result = OpenRouterService.generate(
            messages=[{"role": "user", "content": "Generate a title"}]
        )

        self.assertEqual(result, "Generated response")
        self.assertEqual(
            mock_post.call_args.kwargs["json"]["model"],
            "test/model",
        )

    @patch("apps.ai.services.openrouter_service.httpx.post")
    def test_generate_json_validates_output(self, mock_post):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": ('{"title": "Example", "items": ["A", "B"]}')}}
            ]
        }
        mock_post.return_value = mock_response

        result = OpenRouterService.generate_json(
            messages=[{"role": "user", "content": "Return a JSON object"}],
            serializer_class=ExampleOutputSerializer,
        )

        self.assertEqual(
            result,
            {"title": "Example", "items": ["A", "B"]},
        )

    @patch("apps.ai.services.openrouter_service.httpx.post")
    def test_generate_json_rejects_invalid_schema(self, mock_post):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"title": 123, "items": "bad"}'}}]
        }
        mock_post.return_value = mock_response

        with self.assertRaises(AIStructuredOutputError):
            OpenRouterService.generate_json(
                messages=[{"role": "user", "content": "Return a JSON object"}],
                serializer_class=ExampleOutputSerializer,
            )

    @override_settings(OPENROUTER_API_KEY="")
    def test_missing_api_key_raises_configuration_error(self):
        with self.assertRaises(AIConfigurationError):
            OpenRouterService.generate(messages=[{"role": "user", "content": "Hello"}])

    @patch(
        "apps.ai.services.openrouter_service.httpx.post",
        side_effect=httpx.TimeoutException("Timed out"),
    )
    def test_timeout_raises_provider_timeout_error(self, mock_post):
        with self.assertRaises(AIProviderTimeoutError):
            OpenRouterService.generate(messages=[{"role": "user", "content": "Hello"}])


class TaskBreakdownServiceTests(SimpleTestCase):
    @patch("apps.ai.services.task_breakdown_service.OpenRouterService.generate_json")
    def test_generate_breakdown_returns_validated_result(self, mock_generate):
        expected = {
            "summary": "Implement user login.",
            "subtasks": [
                {
                    "title": "Create login endpoint",
                    "description": "Implement the login API.",
                },
                {
                    "title": "Validate credentials",
                    "description": "Validate submitted credentials.",
                },
                {
                    "title": "Build login form",
                    "description": "Create the frontend login form.",
                },
            ],
        }
        mock_generate.return_value = expected

        result = TaskBreakdownService.generate_breakdown(
            issue_title="Implement user login",
            issue_description="Support email and password authentication.",
        )

        self.assertEqual(result, expected)
        mock_generate.assert_called_once()

    @patch("apps.ai.services.task_breakdown_service.OpenRouterService.generate_json")
    def test_rejects_too_few_subtasks(self, mock_generate):
        mock_generate.return_value = {
            "summary": "Implement login.",
            "subtasks": [
                {"title": "Build login", "description": "Build the login flow."}
            ],
        }

        with self.assertRaises(AIStructuredOutputError):
            TaskBreakdownService.generate_breakdown(issue_title="Implement login")


class TaskBreakdownViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Mock(is_authenticated=True)

    @patch("apps.ai.views.TaskBreakdownService.generate_breakdown")
    def test_returns_generated_breakdown(self, mock_generate):
        mock_generate.return_value = {
            "summary": "Implement login.",
            "subtasks": [
                {
                    "title": "Create login endpoint",
                    "description": "Implement the login API.",
                },
                {
                    "title": "Validate credentials",
                    "description": "Validate submitted credentials.",
                },
                {
                    "title": "Build login form",
                    "description": "Create the frontend login form.",
                },
            ],
        }

        request = self.factory.post(
            "/api/v1/ai/task-breakdown/",
            {
                "issue_title": "Implement user login",
                "issue_description": "Support email authentication.",
            },
            format="json",
        )
        force_authenticate(request, user=self.user)

        response = TaskBreakdownView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["subtasks"]), 3)
        mock_generate.assert_called_once_with(
            issue_title="Implement user login",
            issue_description="Support email authentication.",
        )

    def test_rejects_missing_issue_title(self):
        request = self.factory.post(
            "/api/v1/ai/task-breakdown/",
            {"issue_description": "Implement authentication."},
            format="json",
        )
        force_authenticate(request, user=self.user)

        response = TaskBreakdownView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_unauthenticated_request(self):
        request = self.factory.post(
            "/api/v1/ai/task-breakdown/",
            {"issue_title": "Implement login"},
            format="json",
        )

        response = TaskBreakdownView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FakeProject:
    key = "VUR"


class FakeIssue:
    key = "VUR-10"
    project = FakeProject()
    issue_type = "task"
    title = "Implement user login"
    description = "Support email and password authentication."
    priority = "medium"


class StoryPointEstimationServiceTests(SimpleTestCase):
    @patch(
        "apps.ai.services.story_point_estimation_service.OpenRouterService.generate_json"
    )
    def test_returns_valid_estimate(self, mock_generate):
        expected = {
            "estimated_story_points": 5,
            "rationale": "The task involves backend and frontend work.",
            "assumptions": ["Authentication uses the existing user model."],
            "confidence": "medium",
        }
        mock_generate.return_value = expected

        result = StoryPointEstimationService.estimate(issue=FakeIssue())

        self.assertEqual(result, expected)
        mock_generate.assert_called_once()

    @patch(
        "apps.ai.services.story_point_estimation_service.OpenRouterService.generate_json"
    )
    def test_rejects_unsupported_estimate(self, mock_generate):
        mock_generate.return_value = {
            "estimated_story_points": 4,
            "rationale": "Moderate work.",
            "assumptions": [],
            "confidence": "medium",
        }

        with self.assertRaises(AIStructuredOutputError):
            StoryPointEstimationService.estimate(issue=FakeIssue())


class DuplicateDetectionServiceTests(SimpleTestCase):

    @patch(
        "apps.ai.services.duplicate_detection_service."
        "SearchAccessService.get_allowed_project_ids"
    )
    @patch("apps.ai.services.duplicate_detection_service." "SearchQueryService.search")
    def test_returns_empty_when_no_candidates(self, mock_search, mock_allowed_projects):
        mock_allowed_projects.return_value = {
            "project": [],
            "issue": [12],
            "sprint": [],
        }
        mock_search.return_value = {"total": 0, "results": []}

        result = DuplicateDetectionService.detect(
            user=MagicMock(),
            project_id=12,
            title="Implement authentication",
            description="Add login support.",
        )

        self.assertEqual(result, {"duplicates": []})
        mock_search.assert_called_once()

    @patch(
        "apps.ai.services.duplicate_detection_service."
        "SearchAccessService.get_allowed_project_ids"
    )
    def test_rejects_inaccessible_project(self, mock_allowed_projects):
        mock_allowed_projects.return_value = {
            "project": [],
            "issue": [15],
            "sprint": [],
        }

        with self.assertRaises(PermissionError):
            DuplicateDetectionService.detect(
                user=MagicMock(), project_id=12, title="Implement authentication"
            )

    @patch(
        "apps.ai.services.duplicate_detection_service."
        "OpenRouterService.generate_json"
    )
    @patch("apps.ai.services.duplicate_detection_service." "Issue.objects.filter")
    @patch("apps.ai.services.duplicate_detection_service." "SearchQueryService.search")
    @patch(
        "apps.ai.services.duplicate_detection_service."
        "SearchAccessService.get_allowed_project_ids"
    )
    def test_returns_verified_duplicate(
        self, mock_allowed_projects, mock_search, mock_issue_filter, mock_generate
    ):
        mock_allowed_projects.return_value = {
            "project": [],
            "issue": [12],
            "sprint": [],
        }

        mock_search.return_value = {
            "total": 1,
            "results": [
                {"entity_type": "issue", "entity_id": "42", "project_id": "12"}
            ],
        }

        issue = MagicMock()
        issue.id = 42
        issue.key = "VURN-42"
        issue.title = "Login fails after session expiry"
        issue.description = "Users see an error after the session expires."
        issue.issue_type = "task"
        issue.priority = "medium"

        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = [issue]
        mock_issue_filter.return_value = mock_queryset

        mock_generate.return_value = {
            "duplicates": [
                {
                    "issue_key": "VURN-42",
                    "reason": "Both describe login failures after session expiry.",
                    "confidence": "high",
                }
            ]
        }

        result = DuplicateDetectionService.detect(
            user=MagicMock(),
            project_id=12,
            title="Authentication fails after token expiry",
            description="Login stops working when the token expires.",
        )

        self.assertEqual(len(result["duplicates"]), 1)
        self.assertEqual(result["duplicates"][0]["issue_id"], 42)
        self.assertEqual(result["duplicates"][0]["key"], "VURN-42")
        self.assertEqual(result["duplicates"][0]["confidence"], "high")
        mock_generate.assert_called_once()

    @patch(
        "apps.ai.services.duplicate_detection_service."
        "OpenRouterService.generate_json"
    )
    @patch("apps.ai.services.duplicate_detection_service." "Issue.objects.filter")
    @patch("apps.ai.services.duplicate_detection_service." "SearchQueryService.search")
    @patch(
        "apps.ai.services.duplicate_detection_service."
        "SearchAccessService.get_allowed_project_ids"
    )
    def test_ignores_ai_keys_not_in_candidates(
        self, mock_allowed_projects, mock_search, mock_issue_filter, mock_generate
    ):
        mock_allowed_projects.return_value = {
            "project": [],
            "issue": [12],
            "sprint": [],
        }

        mock_search.return_value = {
            "total": 1,
            "results": [
                {"entity_type": "issue", "entity_id": "42", "project_id": "12"}
            ],
        }

        issue = MagicMock()
        issue.id = 42
        issue.key = "VURN-42"
        issue.title = "Login issue"
        issue.description = "Login fails."
        issue.issue_type = "task"
        issue.priority = "medium"

        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = [issue]
        mock_issue_filter.return_value = mock_queryset

        mock_generate.return_value = {
            "duplicates": [
                {
                    "issue_key": "VURN-999",
                    "reason": "The AI suggested a key not in the candidates.",
                    "confidence": "high",
                }
            ]
        }

        result = DuplicateDetectionService.detect(
            user=MagicMock(),
            project_id=12,
            title="Login fails",
            description="Users cannot log in.",
        )

        self.assertEqual(result, {"duplicates": []})


class SprintSummaryServiceTests(SimpleTestCase):

    def setUp(self):
        self.sprint = SimpleNamespace(
            id=12,
            name="Sprint 4",
            goal="Complete authentication",
            description="Authentication and session handling",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 14),
            estimated_days=10,
            status="completed",
            project=SimpleNamespace(id=5),
        )

        completed_status = SimpleNamespace(category="done")
        incomplete_status = SimpleNamespace(category="in_progress")

        self.completed_issue = SimpleNamespace(
            id=1,
            key="VURN-1",
            title="Implement login",
            description="Add login functionality",
            issue_type="task",
            priority="high",
            story_points=5,
            status=completed_status,
        )

        self.incomplete_issue = SimpleNamespace(
            id=2,
            key="VURN-2",
            title="Implement logout",
            description="Add logout functionality",
            issue_type="task",
            priority="medium",
            story_points=3,
            status=incomplete_status,
        )

    @patch("apps.ai.services.sprint_summary_service.OpenRouterService.generate_json")
    @patch.object(SprintSummaryService, "_get_scope_changes")
    @patch.object(SprintSummaryService, "_get_sprint_issues")
    def test_generates_summary_and_calculates_metrics(
        self, mock_get_issues, mock_get_scope_changes, mock_generate
    ):
        mock_get_issues.return_value = [self.completed_issue, self.incomplete_issue]
        mock_get_scope_changes.return_value = {
            "issues_added": 1,
            "issues_removed": 0,
            "added_issue_keys": ["VURN-2"],
            "removed_issue_keys": [],
        }
        mock_generate.return_value = {
            "summary": "One issue was completed.",
            "achievements": ["Implemented login."],
            "incomplete_work": ["Implement logout."],
            "scope_change_insights": [],
            "risks": [],
            "recommendations": ["Complete logout next."],
        }

        result = SprintSummaryService.generate(sprint=self.sprint)

        self.assertEqual(result["metrics"]["total_issues"], 2)
        self.assertEqual(result["metrics"]["completed_issues"], 1)
        self.assertEqual(result["metrics"]["incomplete_issues"], 1)
        self.assertEqual(result["metrics"]["completion_percentage"], 50)
        self.assertEqual(result["metrics"]["total_story_points"], 8)
        self.assertEqual(result["metrics"]["completed_story_points"], 5)
        self.assertEqual(result["metrics"]["issues_added"], 1)
        self.assertEqual(result["metrics"]["issues_removed"], 0)
        self.assertEqual(result["summary"], "One issue was completed.")
        mock_generate.assert_called_once()

    @patch("apps.ai.services.sprint_summary_service.OpenRouterService.generate_json")
    @patch.object(SprintSummaryService, "_get_scope_changes")
    @patch.object(SprintSummaryService, "_get_sprint_issues")
    def test_handles_sprint_without_issues(
        self, mock_get_issues, mock_get_scope_changes, mock_generate
    ):
        mock_get_issues.return_value = []
        mock_get_scope_changes.return_value = {
            "issues_added": 0,
            "issues_removed": 0,
            "added_issue_keys": [],
            "removed_issue_keys": [],
        }
        mock_generate.return_value = {
            "summary": "No issues were assigned to this sprint.",
            "achievements": [],
            "incomplete_work": [],
            "scope_change_insights": [],
            "risks": [],
            "recommendations": [],
        }

        result = SprintSummaryService.generate(sprint=self.sprint)

        self.assertEqual(result["metrics"]["total_issues"], 0)
        self.assertEqual(result["metrics"]["completion_percentage"], 0)
        self.assertEqual(result["metrics"]["total_story_points"], 0)
        self.assertEqual(result["metrics"]["completed_story_points"], 0)
        mock_generate.assert_called_once()

    def test_identifies_completed_status(self):
        completed_issue = SimpleNamespace(status=SimpleNamespace(category="done"))
        incomplete_issue = SimpleNamespace(
            status=SimpleNamespace(category="in_progress")
        )

        self.assertTrue(SprintSummaryService._is_completed(completed_issue))
        self.assertFalse(SprintSummaryService._is_completed(incomplete_issue))
