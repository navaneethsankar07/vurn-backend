from ..exceptions import AIStructuredOutputError
from ..serializers import StoryPointEstimationResponseSerializer
from .openrouter_service import OpenRouterService
from ..constants import STORY_POINT_PROMPT


class StoryPointEstimationService:

    @classmethod
    def estimate(cls, *, issue):
        issue_context = {
            "issue_key": issue.key,
            "issue_type": issue.issue_type,
            "title": issue.title,
            "description": issue.description or "",
            "priority": issue.priority,
        }

        result = OpenRouterService.generate_json(
            messages=[
                {"role": "system", "content": STORY_POINT_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Estimate the story points for this issue.\n"
                        f"Issue information:\n{issue_context}"
                    ),
                },
            ],
            serializer_class=StoryPointEstimationResponseSerializer,
            temperature=0.2,
            max_tokens=600,
        )

        if result["estimated_story_points"] not in (1, 2, 3, 5, 8, 13):
            raise AIStructuredOutputError(
                "The AI returned an unsupported story-point estimate."
            )

        return result
