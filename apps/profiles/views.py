from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import (
    ChangePasswordSerializer,
    ProfileSerializer,
    UpdateProfileSerializer,
)
from .services.profile_service import ProfileService
from .services.password_service import PasswordService

from .exceptions import InvalidCurrentPasswordException


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get(self, request):
        profile = ProfileService.get_profile(
            request.user,
        )

        serializer = ProfileSerializer(profile)

        return Response(
            serializer.data,
        )

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        user = ProfileService.update_profile(
            request.user,
            serializer.validated_data,
        )

        return Response(
            {
                "message": "Profile updated successfully.",
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "email": user.email,
                    "avatar": user.avatar,
                },
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            PasswordService.change_password(
                user=request.user,
                current_password=serializer.validated_data["current_password"],
                new_password=serializer.validated_data["new_password"],
            )

        except InvalidCurrentPasswordException as exc:
            return Response(
                {
                    "current_password": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Password changed successfully.",
            },
            status=status.HTTP_200_OK,
        )
