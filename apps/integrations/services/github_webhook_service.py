import hashlib
import hmac

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction

from ..exceptions import GitIntegrationException
from ..models import GitRepository, GitWebhookDelivery


class GitHubWebhookService:
    @staticmethod
    def verify_signature(*, payload, signature):
        secret = settings.GITHUB_WEBHOOK_SECRET

        if not secret:
            raise ImproperlyConfigured("GITHUB_WEBHOOK_SECRET is not configured.")

        if not signature or not signature.startswith("sha256="):
            return False

        expected_signature = (
            "sha256="
            + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        )

        return hmac.compare_digest(expected_signature, signature)

    @classmethod
    @transaction.atomic
    def receive_delivery(cls, *, delivery_id, event_type, payload):
        installation_data = payload.get("installation") or {}
        repository_data = payload.get("repository") or {}

        installation_id = installation_data.get("id")
        repository_id = repository_data.get("id")

        if not installation_id or not repository_id:
            raise GitIntegrationException(
                "Webhook payload is missing installation or repository data."
            )

        repository = (
            GitRepository.objects.select_related("integration")
            .filter(
                external_repository_id=str(repository_id),
                integration__provider="github",
                integration__installation__external_installation_id=str(
                    installation_id
                ),
            )
            .first()
        )

        if repository is None:
            raise GitIntegrationException(
                "No connected VURN repository matches this GitHub event."
            )

        try:
            with transaction.atomic():
                delivery, created = GitWebhookDelivery.objects.get_or_create(
                    provider="github",
                    delivery_id=delivery_id,
                    defaults={
                        "integration": repository.integration,
                        "event_type": event_type,
                        "payload": payload,
                        "status": "received",
                    },
                )
        except IntegrityError:
            delivery = GitWebhookDelivery.objects.get(
                provider="github", delivery_id=delivery_id
            )
            created = False

        return {"delivery": delivery, "created": created}
