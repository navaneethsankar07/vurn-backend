from unittest.mock import Mock, patch

import httpx
from django.test import SimpleTestCase, override_settings
from rest_framework import serializers

from apps.ai.exceptions import (
    AIConfigurationError,
    AIProviderTimeoutError,
    AIStructuredOutputError,
)
from apps.ai.services.openrouter_service import OpenRouterService


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
