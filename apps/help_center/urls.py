from django.urls import path

from .views import (
    HelpArticleDetailView,
    HelpArticleListView,
    HelpTopicDetailView,
    HelpTopicListView,
)

urlpatterns = [
    path("topics/", HelpTopicListView.as_view(), name="topic-list"),
    path("topics/<slug:slug>/", HelpTopicDetailView.as_view(), name="topic-detail"),
    path("articles/", HelpArticleListView.as_view(), name="article-list"),
    path(
        "articles/<slug:slug>/", HelpArticleDetailView.as_view(), name="article-detail"
    ),
]
