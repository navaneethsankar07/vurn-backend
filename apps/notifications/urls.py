from django.urls import path

from .views import (
    FCMDeviceRegistrationView,
    FCMDeviceUnregistrationView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationUnreadCountView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path(
        "unread-count/",
        NotificationUnreadCountView.as_view(),
        name="notification-unread-count",
    ),
    path(
        "read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),
    path(
        "<int:notification_id>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),
    path(
        "devices/register/",
        FCMDeviceRegistrationView.as_view(),
        name="fcm-device-register",
    ),
    path(
        "devices/unregister/",
        FCMDeviceUnregistrationView.as_view(),
        name="fcm-device-unregister",
    ),
]
