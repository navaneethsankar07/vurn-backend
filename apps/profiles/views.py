from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProfileSerializer
from .services.profile_service import ProfileService


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = ProfileService.get_profile(
            request.user,
        )

        serializer = ProfileSerializer(profile)

        return Response(
            serializer.data,
        )
