import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..exceptions import GitIntegrationException
from ..services.github_webhook_service import GitHubWebhookService


class GitHubWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.headers.get("X-Hub-Signature-256")
        delivery_id = request.headers.get("X-GitHub-Delivery")
        event_type = request.headers.get("X-GitHub-Event")

        if not delivery_id or not event_type:
            return Response(
                {"error": "Missing GitHub delivery or event headers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not GitHubWebhookService.verify_signature(
            payload=request.body, signature=signature
        ):
            return Response(
                {"error": "Invalid GitHub webhook signature."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                {"error": "Invalid JSON payload."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = GitHubWebhookService.receive_delivery(
                delivery_id=delivery_id, event_type=event_type, payload=payload
            )
        except GitIntegrationException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": (
                    "Webhook delivery already received."
                    if not result["created"]
                    else "Webhook delivery received successfully."
                ),
                "delivery_id": delivery_id,
                "event": event_type,
                "duplicate": not result["created"],
            },
            status=status.HTTP_200_OK,
        )
