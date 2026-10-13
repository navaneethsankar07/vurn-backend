from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.help_center.constants import HELP_TOPICS
from apps.help_center.serializers import (
    HelpTopicDetailSerializer,
    HelpTopicListSerializer,
)


class HelpTopicListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip().casefold()

        topics = list(HELP_TOPICS.values())

        if query:
            topics = [
                topic
                for topic in topics
                if query in topic["title"].casefold()
                or query in topic["description"].casefold()
                or query in topic["slug"].casefold()
            ]

        serializer = HelpTopicListSerializer(topics, many=True)

        return Response({"results": serializer.data})


class HelpTopicDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        topic = HELP_TOPICS.get(slug)

        if topic is None:
            return Response(
                {"detail": "Help topic not found."},
                status=404,
            )

        serializer = HelpTopicDetailSerializer(topic)

        return Response(serializer.data)
