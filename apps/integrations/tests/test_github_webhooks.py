import hashlib
import hmac
import json
from unittest.mock import MagicMock, patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from django.test import SimpleTestCase, TestCase, override_settings
from ..services.github_webhook_service import GitHubWebhookService
from ..services.github_webhook_processor import GitHubWebhookProcessor


@override_settings(GITHUB_WEBHOOK_SECRET="test-webhook-secret")
class GitHubWebhookSignatureTests(TestCase):
    def setUp(self):
        self.payload = json.dumps({"action": "opened"}).encode("utf-8")

        digest = hmac.new(
            b"test-webhook-secret", self.payload, hashlib.sha256
        ).hexdigest()

        self.signature = f"sha256={digest}"

    def test_valid_signature_is_accepted(self):
        self.assertTrue(
            GitHubWebhookService.verify_signature(
                payload=self.payload, signature=self.signature
            )
        )

    def test_invalid_signature_is_rejected(self):
        self.assertFalse(
            GitHubWebhookService.verify_signature(
                payload=self.payload, signature="sha256=invalid"
            )
        )

    def test_missing_signature_is_rejected(self):
        self.assertFalse(
            GitHubWebhookService.verify_signature(payload=self.payload, signature=None)
        )

    def test_modified_payload_is_rejected(self):
        self.assertFalse(
            GitHubWebhookService.verify_signature(
                payload=b'{"action":"closed"}', signature=self.signature
            )
        )

    @override_settings(GITHUB_WEBHOOK_SECRET=None)
    def test_missing_secret_raises_configuration_error(self):
        with self.assertRaises(ImproperlyConfigured):
            GitHubWebhookService.verify_signature(
                payload=self.payload, signature=self.signature
            )


class GitHubWebhookDeliveryTests(TestCase):
    @patch(
        "apps.integrations.services.github_webhook_service."
        "GitWebhookDelivery.objects.get_or_create"
    )
    @patch(
        "apps.integrations.services.github_webhook_service."
        "GitRepository.objects.filter"
    )
    def test_duplicate_delivery_is_not_created_again(
        self, mock_repository_filter, mock_get_or_create
    ):
        repository = MagicMock()
        repository.integration = MagicMock()

        queryset = MagicMock()
        queryset.select_related.return_value = queryset
        queryset.first.return_value = repository
        mock_repository_filter.return_value = queryset

        existing_delivery = MagicMock()
        existing_delivery.status = "processed"
        mock_get_or_create.return_value = (existing_delivery, False)

        result = GitHubWebhookService.receive_delivery(
            delivery_id="delivery-123",
            event_type="issues",
            payload={"installation": {"id": 10}, "repository": {"id": 20}},
        )

        self.assertFalse(result["created"])
        self.assertIs(result["delivery"], existing_delivery)
        mock_get_or_create.assert_called_once()


class GitHubWebhookProcessorTests(TestCase):
    @patch.object(GitHubWebhookProcessor, "_get_matching_repositories")
    @patch.object(GitHubWebhookProcessor, "_sync_commits")
    def test_push_event_syncs_commits_for_each_repository(
        self, mock_sync_commits, mock_get_repositories
    ):
        repository_one = MagicMock()
        repository_two = MagicMock()
        mock_get_repositories.return_value = [repository_one, repository_two]

        delivery = MagicMock()
        delivery.event_type = "push"
        delivery.payload = {"commits": []}

        GitHubWebhookProcessor.process_delivery(delivery=delivery)

        self.assertEqual(mock_sync_commits.call_count, 2)
        self.assertEqual(delivery.status, "processed")
        self.assertIsNone(delivery.error_message)
        delivery.save.assert_called_once()

    @patch.object(GitHubWebhookProcessor, "_get_matching_repositories")
    @patch.object(
        GitHubWebhookProcessor,
        "_sync_issue",
        side_effect=ValueError("Synchronization failed"),
    )
    def test_failed_event_is_marked_failed(
        self, mock_sync_issue, mock_get_repositories
    ):
        mock_get_repositories.return_value = [MagicMock()]

        delivery = MagicMock()
        delivery.event_type = "issues"
        delivery.payload = {}

        with self.assertRaisesMessage(ValueError, "Synchronization failed"):
            GitHubWebhookProcessor.process_delivery(delivery=delivery)

        self.assertEqual(delivery.status, "failed")
        self.assertEqual(delivery.error_message, "Synchronization failed")
        delivery.save.assert_called_once()

    @patch.object(GitHubWebhookProcessor, "_get_matching_repositories", return_value=[])
    def test_delivery_without_matching_repository_fails(self, mock_get_repositories):
        delivery = MagicMock()
        delivery.event_type = "push"
        delivery.payload = {}

        with self.assertRaisesMessage(
            ValueError, "No connected VURN repositories match this delivery."
        ):
            GitHubWebhookProcessor.process_delivery(delivery=delivery)

        self.assertEqual(delivery.status, "failed")

    @patch.object(GitHubWebhookProcessor, "_get_matching_repositories")
    @patch.object(GitHubWebhookProcessor, "_sync_pull_request")
    def test_pull_request_event_is_dispatched(
        self, mock_sync_pull_request, mock_get_repositories
    ):
        repository = MagicMock()
        mock_get_repositories.return_value = [repository]

        delivery = MagicMock()
        delivery.event_type = "pull_request"
        delivery.payload = {"action": "opened"}

        GitHubWebhookProcessor.process_delivery(delivery=delivery)

        mock_sync_pull_request.assert_called_once_with(
            repository=repository, payload=delivery.payload
        )

    @patch.object(GitHubWebhookProcessor, "_get_matching_repositories")
    @patch.object(GitHubWebhookProcessor, "_sync_issue")
    def test_issue_event_is_dispatched(self, mock_sync_issue, mock_get_repositories):
        repository = MagicMock()
        mock_get_repositories.return_value = [repository]

        delivery = MagicMock()
        delivery.event_type = "issues"
        delivery.payload = {"action": "opened"}

        GitHubWebhookProcessor.process_delivery(delivery=delivery)

        mock_sync_issue.assert_called_once_with(
            repository=repository, payload=delivery.payload
        )

    @patch(
        "apps.integrations.services.github_webhook_processor."
        "GitIssue.objects.update_or_create"
    )
    def test_issue_event_updates_local_issue(self, mock_update):
        repository = MagicMock()

        GitHubWebhookProcessor._sync_issue(
            repository=repository,
            payload={
                "action": "opened",
                "issue": {
                    "id": 101,
                    "number": 12,
                    "title": "Fix login",
                    "body": "Login fails",
                    "state": "open",
                    "html_url": "https://github.com/acme/app/issues/12",
                    "created_at": "2026-10-09T08:00:00Z",
                    "updated_at": "2026-10-09T08:30:00Z",
                    "closed_at": None,
                    "user": {"login": "developer"},
                },
            },
        )

        mock_update.assert_called_once_with(
            repository=repository,
            issue_number=12,
            defaults={
                "external_id": 101,
                "title": "Fix login",
                "description": "Login fails",
                "state": "open",
                "author_username": "developer",
                "url": "https://github.com/acme/app/issues/12",
                "opened_at": "2026-10-09T08:00:00Z",
                "closed_at": None,
                "created_at": "2026-10-09T08:00:00Z",
                "updated_at": "2026-10-09T08:30:00Z",
            },
        )

    @patch(
        "apps.integrations.services.github_webhook_processor."
        "GitPullRequest.objects.update_or_create"
    )
    def test_merged_pull_request_is_stored_as_merged(self, mock_update):
        repository = MagicMock()

        GitHubWebhookProcessor._sync_pull_request(
            repository=repository,
            payload={
                "action": "closed",
                "pull_request": {
                    "id": 202,
                    "number": 7,
                    "title": "Add login",
                    "body": "Login feature",
                    "state": "closed",
                    "created_at": "2026-10-08T10:00:00Z",
                    "closed_at": "2026-10-09T08:00:00Z",
                    "merged_at": "2026-10-09T08:00:00Z",
                    "html_url": "https://github.com/acme/app/pull/7",
                    "draft": False,
                    "user": {"login": "developer"},
                    "head": {"ref": "feature/login"},
                    "base": {"ref": "main"},
                },
            },
        )

        _, kwargs = mock_update.call_args

        self.assertEqual(kwargs["defaults"]["state"], "merged")
        self.assertEqual(kwargs["defaults"]["source_branch"], "feature/login")
        self.assertEqual(kwargs["defaults"]["target_branch"], "main")

    @patch(
        "apps.integrations.services.github_webhook_processor."
        "GitCommit.objects.update_or_create"
    )
    def test_push_event_stores_commit(self, mock_update):
        repository = MagicMock()

        GitHubWebhookProcessor._sync_commits(
            repository=repository,
            payload={
                "ref": "refs/heads/main",
                "commits": [
                    {
                        "id": "abc123",
                        "message": "Fix login",
                        "timestamp": "2026-10-09T08:00:00Z",
                        "url": "https://github.com/acme/app/commit/abc123",
                        "author": {"name": "Developer", "email": "dev@example.com"},
                    }
                ],
            },
        )

        mock_update.assert_called_once()

        _, kwargs = mock_update.call_args

        self.assertEqual(kwargs["sha"], "abc123")
        self.assertEqual(kwargs["defaults"]["branch"], "main")
        self.assertEqual(kwargs["defaults"]["message"], "Fix login")

    @patch.object(GitHubWebhookProcessor, "_get_matching_repositories")
    @patch.object(
        GitHubWebhookProcessor,
        "_sync_issue",
        side_effect=[ValueError("Temporary failure"), None],
    )
    def test_failed_delivery_can_be_retried(
        self, mock_sync_issue, mock_get_repositories
    ):
        mock_get_repositories.return_value = [MagicMock()]

        delivery = MagicMock()
        delivery.event_type = "issues"
        delivery.payload = {"action": "opened"}

        with self.assertRaisesMessage(ValueError, "Temporary failure"):
            GitHubWebhookProcessor.process_delivery(delivery=delivery)

        self.assertEqual(delivery.status, "failed")

        GitHubWebhookProcessor.process_delivery(delivery=delivery)

        self.assertEqual(delivery.status, "processed")
        self.assertIsNone(delivery.error_message)
        self.assertEqual(mock_sync_issue.call_count, 2)
