from django.db import transaction
from django.utils import timezone

from ..models import Notification, NotificationType
from apps.projects.models import ProjectMember
from .push_delivery_service import PushDeliveryService


class NotificationService:
    @staticmethod
    def create_notification(
        *,
        user,
        notification_type,
        title,
        message,
        organization=None,
        invitation=None,
        project=None,
        issue=None,
        sprint=None
    ):
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            organization=organization,
            invitation=invitation,
            project=project,
            issue=issue,
            sprint=sprint,
        )

        transaction.on_commit(
            lambda notification_id=notification.id: (
                PushDeliveryService.send_notification(
                    notification=Notification.objects.get(id=notification_id)
                )
            )
        )

        return notification

    @staticmethod
    def notify_project_members(
        *,
        project,
        notification_type,
        title,
        message,
        actor=None,
        issue=None,
        sprint=None
    ):
        recipient_ids = ProjectMember.objects.filter(project=project).values_list(
            "user_id", flat=True
        )

        if actor is not None:
            recipient_ids = recipient_ids.exclude(user_id=actor.id)

        notifications = [
            Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                project=project,
                issue=issue,
                sprint=sprint,
            )
            for user_id in set(recipient_ids)
        ]

        if notifications:
            Notification.objects.bulk_create(notifications)

            for notification in notifications:
                transaction.on_commit(
                    lambda notification_id=notification.id: PushDeliveryService.send_notification(
                        notification=Notification.objects.get(id=notification_id)
                    )
                )

        return len(notifications)

    @staticmethod
    @transaction.atomic
    def mark_as_read(*, notification_id, user):
        notification = (
            Notification.objects.select_for_update()
            .filter(id=notification_id, user=user)
            .first()
        )

        if notification is None:
            return None

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])

        return notification

    @staticmethod
    def mark_all_as_read(*, user):
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

    @staticmethod
    def get_unread_count(*, user):
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def list_notifications(*, user):
        return Notification.objects.filter(user=user).select_related(
            "organization", "invitation", "project", "issue", "sprint"
        )
