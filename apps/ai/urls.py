from django.urls import path

from .views import StoryPointEstimationView, TaskBreakdownView

urlpatterns = [
    path("task-breakdown/", TaskBreakdownView.as_view(), name="ai-task-breakdown"),
    path(
        "estimate-story-points/",
        StoryPointEstimationView.as_view(),
        name="issue-estimate-story-points",
    ),
]
