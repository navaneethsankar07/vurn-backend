from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FCMDeviceRegistrationSerializer, NotificationSerializer

from .services.notification_service import NotificationService
from .services.fcm_device_service import FCMDeviceService


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = NotificationService.list_notifications(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)

        return Response(
            {
                "unread_count": NotificationService.get_unread_count(user=request.user),
                "results": serializer.data,
            }
        )


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {"unread_count": NotificationService.get_unread_count(user=request.user)}
        )


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):
        notification = NotificationService.mark_as_read(
            notification_id=notification_id, user=request.user
        )

        if notification is None:
            return Response(
                {"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        updated_count = NotificationService.mark_all_as_read(user=request.user)

        return Response({"updated_count": updated_count})


class FCMDeviceRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FCMDeviceRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device = FCMDeviceService.register_device(
            user=request.user, token=serializer.validated_data["token"]
        )

        return Response(
            {"registered": True, "device_id": device.id}, status=status.HTTP_200_OK
        )


class FCMDeviceUnregistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = FCMDeviceRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_count = FCMDeviceService.unregister_device(
            user=request.user, token=serializer.validated_data["token"]
        )

        return Response({"unregistered": updated_count > 0})
