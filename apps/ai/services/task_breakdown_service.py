from apps.ai.exceptions import AIStructuredOutputError
from apps.ai.serializers import TaskBreakdownResponseSerializer
from apps.ai.services.openrouter_service import OpenRouterService

from ..constants import SYSTEM_PROMPT


class TaskBreakdownService:

    @classmethod
    def generate_breakdown(
        cls, *, issue_title: str, issue_description: str = ""
    ) -> dict:
        title = issue_title.strip()
        description = issue_description.strip()

        if not title:
            raise ValueError("Issue title cannot be empty.")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Break down the following engineering task.\n\n"
                    f"Issue title:\n{title}\n\n"
                    f"Issue description:\n"
                    f"{description or 'No description provided.'}\n\n"
                    "Return between 3 and 8 actionable subtasks."
                ),
            },
        ]

        result = OpenRouterService.generate_json(
            messages=messages,
            serializer_class=TaskBreakdownResponseSerializer,
            temperature=0.2,
            max_tokens=1200,
        )

        if not 3 <= len(result["subtasks"]) <= 8:
            raise AIStructuredOutputError(
                "The AI returned an invalid number of subtasks."
            )

        return result
