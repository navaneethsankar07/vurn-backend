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


class GlobalSearchView(APIView):
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

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(
                request.query_params.get(
                    "page_size",
                    SearchQueryService.DEFAULT_PAGE_SIZE,
                )
            )
        except (TypeError, ValueError):
            return Response(
                {"detail": "Page and page_size must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if page < 1 or page_size < 1:
            return Response(
                {"detail": "Page and page_size must be positive integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        page_size = min(
            page_size,
            SearchQueryService.MAX_PAGE_SIZE,
        )

        allowed_project_ids = SearchAccessService.get_allowed_project_ids(
            user=request.user,
        )

        result = SearchQueryService.search(
            query=query,
            allowed_project_ids=allowed_project_ids,
            page=page,
            page_size=page_size,
        )

        return Response(
            {
                "query": query,
                "page": page,
                "page_size": page_size,
                "total": result["total"],
                "results": result["results"],
            },
            status=status.HTTP_200_OK,
        )
