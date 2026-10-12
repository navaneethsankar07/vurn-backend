from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.search.services.access_service import SearchAccessService
from apps.search.services.query_service import SearchQueryService


class SearchSuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if len(query) < 2:
            return Response(
                {
                    "detail": "Search query must contain at least 2 characters.",
                    "results": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_project_ids = SearchAccessService.get_allowed_project_ids(
            user=request.user,
        )

        result = SearchQueryService.get_suggestions(
            query=query,
            allowed_project_ids=allowed_project_ids,
        )

        return Response(result, status=status.HTTP_200_OK)
