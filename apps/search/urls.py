from django.urls import path

from apps.search.views import SearchSuggestionsView

app_name = "search"

urlpatterns = [
    path(
        "suggestions/",
        SearchSuggestionsView.as_view(),
        name="suggestions",
    ),
]
