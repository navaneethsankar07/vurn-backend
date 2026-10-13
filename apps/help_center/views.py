from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from .serializers import (
    FAQSerializer,
    HelpArticleDetailSerializer,
    HelpArticleListSerializer,
    HelpTopicDetailSerializer,
    HelpTopicListSerializer,
)
from .constants.faq_constants import FAQ_ITEMS
from .constants.article_constants import POPULAR_ARTICLES
from .constants.quick_actions_constants import HELP_TOPICS


class HelpTopicListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip().casefold()
        limit_param = request.query_params.get("limit")

        if limit_param is not None:
            try:
                limit = int(limit_param)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "Limit must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if limit < 1:
                return Response(
                    {"detail": "Limit must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            limit = None

        topics = list(HELP_TOPICS.values())

        if query:
            topics = [
                topic
                for topic in topics
                if query in topic["title"].casefold()
                or query in topic["description"].casefold()
                or query in topic["slug"].casefold()
            ]

        if limit is not None:
            topics = topics[:limit]

        serializer = HelpTopicListSerializer(topics, many=True)

        return Response({"results": serializer.data})


class HelpTopicDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        topic = HELP_TOPICS.get(slug)

        if topic is None:
            return Response(
                {"detail": "Help topic not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = HelpTopicDetailSerializer(topic)

        return Response(serializer.data)


class HelpArticleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip().casefold()
        category = request.query_params.get("category", "").strip().casefold()

        articles = list(POPULAR_ARTICLES.values())

        if query:
            articles = [
                article
                for article in articles
                if query in article["title"].casefold()
                or query in article["description"].casefold()
                or query in article["category"].casefold()
                or query in article["slug"].casefold()
            ]

        if category:
            articles = [
                article
                for article in articles
                if article["category"].casefold() == category
            ]

        serializer = HelpArticleListSerializer(articles, many=True)

        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class HelpArticleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        article = POPULAR_ARTICLES.get(slug)

        if article is None:
            return Response(
                {"detail": "Help article not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = HelpArticleDetailSerializer(article)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FAQListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = FAQSerializer(FAQ_ITEMS, many=True)

        return Response({"results": serializer.data})
