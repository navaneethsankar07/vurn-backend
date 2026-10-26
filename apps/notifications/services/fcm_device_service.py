from django.utils import timezone

from apps.notifications.models import FCMDevice


class FCMDeviceService:
    @staticmethod
    def register_device(*, user, token):
        device, _ = FCMDevice.objects.update_or_create(
            token=token,
            defaults={"user": user, "is_active": True, "last_used_at": timezone.now()},
        )

        return device

    @staticmethod
    def unregister_device(*, user, token):
        return FCMDevice.objects.filter(user=user, token=token, is_active=True).update(
            is_active=False
        )
