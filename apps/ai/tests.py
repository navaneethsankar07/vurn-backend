from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.ai.views import (
    TaskBreakdownView,
    StoryPointEstimationView,
    DuplicateIssueDetectionView,
    SprintSummaryView,
    ReleaseNotesView,
)


class AIFeatureViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = MagicMock()
        self.user.is_authenticated = True
        self.user.id = 1

        self.organization = SimpleNamespace(id=1, slug="test-org")

        self.project = SimpleNamespace(id=10, slug="test-project")

        self.issue = SimpleNamespace(
            id=20,
            key="TEST-20",
            issue_type="task",
            title="Implement authentication",
            description="Add JWT authentication",
            priority="high",
        )

        self.sprint = SimpleNamespace(id=30, project=self.project)

        self.repository = SimpleNamespace(id=40, name="test-repository")

    def call_view(self, view_class, data):
        request = self.factory.post("/api/v1/ai/test/", data, format="json")
        force_authenticate(request, user=self.user)
        return view_class.as_view()(request)

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.TaskBreakdownService.generate_breakdown")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_task_breakdown_success(
        self, mock_get_organization, mock_generate, mock_consume
    ):
        mock_get_organization.return_value = self.organization
        mock_generate.return_value = {
            "summary": "Implement authentication",
            "subtasks": [
                {"title": "Create models", "description": "Define models"},
                {"title": "Add API", "description": "Create endpoints"},
                {"title": "Write tests", "description": "Test endpoints"},
            ],
        }

        response = self.call_view(
            TaskBreakdownView,
            {
                "organization_slug": "test-org",
                "issue_title": "Implement authentication",
                "issue_description": "Add JWT authentication",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_consume.assert_called_once_with(
            organization=self.organization, user=self.user, feature="task_breakdown"
        )

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.TaskBreakdownService.generate_breakdown")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_task_breakdown_failure_does_not_consume_credits(
        self, mock_get_organization, mock_generate, mock_consume
    ):
        from apps.ai.exceptions import AIProviderError

        mock_get_organization.return_value = self.organization
        mock_generate.side_effect = AIProviderError("Provider failed")

        response = self.call_view(
            TaskBreakdownView,
            {
                "organization_slug": "test-org",
                "issue_title": "Implement authentication",
                "issue_description": "Add JWT authentication",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        mock_consume.assert_not_called()

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.StoryPointEstimationService.estimate")
    @patch("apps.ai.views.IssueService.get_issue_by_id")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_story_point_estimation_success(
        self, mock_get_organization, mock_get_issue, mock_estimate, mock_consume
    ):
        mock_get_organization.return_value = self.organization
        mock_get_issue.return_value = self.issue
        mock_estimate.return_value = {
            "estimated_story_points": 5,
            "rationale": "Moderate complexity",
            "assumptions": ["Existing project setup"],
            "confidence": "high",
        }

        response = self.call_view(
            StoryPointEstimationView, {"organization_slug": "test-org", "issue_id": 20}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_consume.assert_called_once_with(
            organization=self.organization,
            user=self.user,
            feature="story_point_estimation",
        )

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.StoryPointEstimationService.estimate")
    @patch("apps.ai.views.IssueService.get_issue_by_id")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_story_point_estimation_failure_does_not_consume_credits(
        self, mock_get_organization, mock_get_issue, mock_estimate, mock_consume
    ):
        from apps.ai.exceptions import AIProviderError

        mock_get_organization.return_value = self.organization
        mock_get_issue.return_value = self.issue
        mock_estimate.side_effect = AIProviderError("Provider failed")

        response = self.call_view(
            StoryPointEstimationView, {"organization_slug": "test-org", "issue_id": 20}
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        mock_consume.assert_not_called()

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.DuplicateDetectionService.detect")
    @patch("apps.ai.views.ProjectService.get_project")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_duplicate_detection_success(
        self, mock_get_organization, mock_get_project, mock_detect, mock_consume
    ):
        mock_get_organization.return_value = self.organization
        mock_get_project.return_value = self.project
        mock_detect.return_value = {"duplicates": []}

        response = self.call_view(
            DuplicateIssueDetectionView,
            {
                "organization_slug": "test-org",
                "project_slug": "test-project",
                "title": "Implement authentication",
                "description": "Add JWT authentication",
                "issue_type": "task",
                "priority": "medium",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_consume.assert_called_once_with(
            organization=self.organization,
            user=self.user,
            feature="duplicate_issue_detection",
        )

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.DuplicateDetectionService.detect")
    @patch("apps.ai.views.ProjectService.get_project")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_duplicate_detection_failure_does_not_consume_credits(
        self, mock_get_organization, mock_get_project, mock_detect, mock_consume
    ):
        from apps.ai.exceptions import AIProviderError

        mock_get_organization.return_value = self.organization
        mock_get_project.return_value = self.project
        mock_detect.side_effect = AIProviderError("Provider failed")

        response = self.call_view(
            DuplicateIssueDetectionView,
            {
                "organization_slug": "test-org",
                "project_slug": "test-project",
                "title": "Implement authentication",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        mock_consume.assert_not_called()

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.SprintSummaryService.generate")
    @patch("apps.ai.views.Sprint.objects.filter")
    @patch("apps.ai.views.ProjectService.get_project")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_sprint_summary_success(
        self,
        mock_get_organization,
        mock_get_project,
        mock_sprint_filter,
        mock_generate,
        mock_consume,
    ):
        mock_get_organization.return_value = self.organization
        mock_get_project.return_value = self.project
        mock_sprint_filter.return_value.first.return_value = self.sprint
        mock_generate.return_value = {
            "summary": "Sprint completed successfully",
            "achievements": [],
            "incomplete_work": [],
            "scope_change_insights": [],
            "risks": [],
            "recommendations": [],
        }

        response = self.call_view(
            SprintSummaryView,
            {
                "organization_slug": "test-org",
                "project_slug": "test-project",
                "sprint_id": 30,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_consume.assert_called_once_with(
            organization=self.organization, user=self.user, feature="sprint_summary"
        )

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.SprintSummaryService.generate")
    @patch("apps.ai.views.Sprint.objects.filter")
    @patch("apps.ai.views.ProjectService.get_project")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_sprint_summary_failure_does_not_consume_credits(
        self,
        mock_get_organization,
        mock_get_project,
        mock_sprint_filter,
        mock_generate,
        mock_consume,
    ):
        from apps.ai.exceptions import AIProviderError

        mock_get_organization.return_value = self.organization
        mock_get_project.return_value = self.project
        mock_sprint_filter.return_value.first.return_value = self.sprint
        mock_generate.side_effect = AIProviderError("Provider failed")

        response = self.call_view(
            SprintSummaryView,
            {
                "organization_slug": "test-org",
                "project_slug": "test-project",
                "sprint_id": 30,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        mock_consume.assert_not_called()

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.ReleaseNotesService.generate")
    @patch("apps.ai.views.GitRepository.objects.filter")
    @patch("apps.ai.views.ProjectService.get_project")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_release_notes_success(
        self,
        mock_get_organization,
        mock_get_project,
        mock_repository_filter,
        mock_generate,
        mock_consume,
    ):
        mock_get_organization.return_value = self.organization
        mock_get_project.return_value = self.project
        mock_repository_filter.return_value.first.return_value = self.repository
        mock_generate.return_value = {
            "release_notes": {
                "title": "Test Release",
                "overview": "Release overview",
                "highlights": [],
                "bug_fixes": [],
                "improvements": [],
                "breaking_changes": [],
                "known_issues": [],
                "technical_changes": [],
                "markdown": "# Test Release",
            },
            "source_summary": {
                "commits_analyzed": 1,
                "merged_pull_requests_analyzed": 1,
            },
        }

        response = self.call_view(
            ReleaseNotesView,
            {
                "organization_slug": "test-org",
                "project_slug": "test-project",
                "repository_id": 40,
                "start_date": "2026-10-01",
                "end_date": "2026-10-24",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_consume.assert_called_once_with(
            organization=self.organization, user=self.user, feature="release_notes"
        )

    @patch("apps.ai.views.OrganizationAIWalletService.consume_credits")
    @patch("apps.ai.views.ReleaseNotesService.generate")
    @patch("apps.ai.views.GitRepository.objects.filter")
    @patch("apps.ai.views.ProjectService.get_project")
    @patch("apps.ai.views.OrganizationService.get_user_organization")
    def test_release_notes_failure_does_not_consume_credits(
        self,
        mock_get_organization,
        mock_get_project,
        mock_repository_filter,
        mock_generate,
        mock_consume,
    ):
        from apps.ai.exceptions import AIProviderError

        mock_get_organization.return_value = self.organization
        mock_get_project.return_value = self.project
        mock_repository_filter.return_value.first.return_value = self.repository
        mock_generate.side_effect = AIProviderError("Provider failed")

        response = self.call_view(
            ReleaseNotesView,
            {
                "organization_slug": "test-org",
                "project_slug": "test-project",
                "repository_id": 40,
                "start_date": "2026-10-01",
                "end_date": "2026-10-24",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        mock_consume.assert_not_called()
