import json
import logging
from typing import Any

import httpx
from django.conf import settings
from rest_framework import serializers

from apps.ai.exceptions import (
    AIConfigurationError,
    AIProviderError,
    AIProviderTimeoutError,
    AIResponseError,
    AIStructuredOutputError,
)

logger = logging.getLogger(__name__)


class OpenRouterService:
    @staticmethod
    def _get_configuration():
        api_key = settings.OPENROUTER_API_KEY
        model = settings.OPENROUTER_MODEL
        base_url = settings.OPENROUTER_BASE_URL
        timeout = settings.OPENROUTER_TIMEOUT
        max_tokens = settings.OPENROUTER_MAX_TOKENS

        if not api_key or not model:
            raise AIConfigurationError(
                "OpenRouter API key and model must be configured."
            )

        if not base_url.startswith("https://"):
            raise AIConfigurationError("OpenRouter base URL must use HTTPS.")

        if timeout <= 0 or max_tokens <= 0:
            raise AIConfigurationError(
                "OpenRouter timeout and max tokens must be positive."
            )

        return api_key, model, base_url, timeout, max_tokens

    @classmethod
    def generate(
        cls,
        *,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        api_key, model, base_url, timeout, configured_max_tokens = (
            cls._get_configuration()
        )

        if not messages:
            raise ValueError("At least one message is required.")

        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2.")

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": (
                max_tokens if max_tokens is not None else configured_max_tokens
            ),
        }

        if payload["max_tokens"] <= 0:
            raise ValueError("max_tokens must be positive.")

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except httpx.TimeoutException as exc:
            logger.warning("OpenRouter request timed out.")
            raise AIProviderTimeoutError("The AI provider request timed out.") from exc
        except httpx.RequestError as exc:
            logger.warning(
                "OpenRouter connection failed: %s",
                type(exc).__name__,
            )
            raise AIProviderError("Could not connect to the AI provider.") from exc

        if not response.is_success:
            logger.warning(
                "OpenRouter returned HTTP status %s.",
                response.status_code,
            )
            raise AIProviderError(
                f"The AI provider returned HTTP {response.status_code}."
            )

        try:
            response_data = response.json()
            choices = response_data.get("choices", [])

            if not choices or not isinstance(choices[0], dict):
                raise AIResponseError("The AI provider returned no completion choices.")

            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content")
            finish_reason = choice.get("finish_reason")

        except (ValueError, TypeError) as exc:
            raise AIResponseError(
                "The AI provider returned an unexpected response."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            logger.warning(
                "OpenRouter returned empty content. Model=%s, finish_reason=%s",
                response_data.get("model"),
                finish_reason,
            )
            raise AIResponseError(
                f"The AI provider returned empty content "
                f"(finish_reason={finish_reason})."
            )

        return content.strip()

    @classmethod
    def generate_json(
        cls,
        *,
        messages: list[dict[str, str]],
        serializer_class: type[serializers.Serializer],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        content = cls.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )

        try:
            parsed_data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIStructuredOutputError(
                "The AI provider did not return valid JSON."
            ) from exc

        if not isinstance(parsed_data, dict):
            raise AIStructuredOutputError("The AI response must be a JSON object.")

        serializer = serializer_class(data=parsed_data)

        if not serializer.is_valid():
            logger.warning(
                "AI response failed schema validation. Invalid fields: %s",
                list(serializer.errors.keys()),
            )
            raise AIStructuredOutputError(
                "The AI response did not match the required schema."
            )

        return dict(serializer.validated_data)
