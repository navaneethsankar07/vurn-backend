from django.urls import path

from apps.help_center.views import (
    HelpTopicDetailView,
    HelpTopicListView,
)

app_name = "help_center"

urlpatterns = [
    path(
        "topics/",
        HelpTopicListView.as_view(),
        name="topic-list",
    ),
    path(
        "topics/<slug:slug>/",
        HelpTopicDetailView.as_view(),
        name="topic-detail",
    ),
]
