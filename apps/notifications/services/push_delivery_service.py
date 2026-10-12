import logging

from django.conf import settings
from firebase_admin import exceptions as firebase_exceptions
from firebase_admin import messaging

from apps.notifications.models import FCMDevice
from apps.notifications.services.firebase_service import FirebasePushService

logger = logging.getLogger(__name__)


class PushDeliveryService:
    @staticmethod
    def send_notification(*, notification):
        devices = FCMDevice.objects.filter(user=notification.user, is_active=True)

        logger.info(
            "[FCM] Delivery started | notification=%s recipient=%s devices=%s",
            notification.id,
            notification.user_id,
            devices.count(),
        )

        for device in devices.iterator():
            try:
                message_id = FirebasePushService.send_to_token(
                    token=device.token,
                    title=notification.title,
                    body=notification.message,
                    data={
                        "notification_id": notification.id,
                        "type": notification.type,
                        "url": PushDeliveryService._get_notification_url(notification),
                    },
                )

                logger.info(
                    "[FCM] Message accepted | notification=%s device=%s message_id=%s",
                    notification.id,
                    device.id,
                    message_id,
                )

            except messaging.UnregisteredError:
                device.is_active = False
                device.save(update_fields=["is_active"])

                logger.warning(
                    "[FCM] Invalid token deactivated | notification=%s device=%s",
                    notification.id,
                    device.id,
                )

            except (firebase_exceptions.FirebaseError, RuntimeError):
                logger.exception(
                    "[FCM] Delivery failed | notification=%s device=%s",
                    notification.id,
                    device.id,
                )

    @staticmethod
    def _get_notification_url(notification):
        organization = notification.organization

        if notification.issue_id:
            issue = notification.issue
            project = issue.project
            organization = project.organization
            return (
                f"{PushDeliveryService._get_frontend_url(organization.slug)}"
                f"/projects/{project.slug}/issues?selectedIssue={issue.id}"
            )

        if notification.sprint_id:
            sprint = notification.sprint
            project = sprint.project
            organization = project.organization
            return (
                f"{PushDeliveryService._get_frontend_url(organization.slug)}"
                f"/projects/{project.slug}/sprints/{sprint.id}"
            )

        if notification.project_id:
            project = notification.project
            organization = project.organization
            return (
                f"{PushDeliveryService._get_frontend_url(organization.slug)}"
                f"/projects/{project.slug}"
            )

        if notification.invitation_id:
            return (
                f"{PushDeliveryService._get_frontend_url(organization.slug)}"
                "/organizations/invitations"
            )

        if organization:
            return f"{PushDeliveryService._get_frontend_url(organization.slug)}" "/"

        return settings.FRONTEND_URL.rstrip("/") + "/"

    @staticmethod
    def _get_frontend_url(organization_slug):
        frontend_url = settings.FRONTEND_URL.rstrip("/")
        scheme, separator, domain = frontend_url.partition("://")

        if separator:
            return f"{scheme}://{organization_slug}.{domain}"

        return f"{organization_slug}.{frontend_url}"
