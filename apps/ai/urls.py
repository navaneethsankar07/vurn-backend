from django.urls import path

from .views import (
    TaskBreakdownView,
    StoryPointEstimationView,
    DuplicateIssueDetectionView,
)

urlpatterns = [
    path("task-breakdown/", TaskBreakdownView.as_view(), name="ai-task-breakdown"),
    path(
        "estimate-story-points/",
        StoryPointEstimationView.as_view(),
        name="issue-estimate-story-points",
    ),
    path(
        "detect-duplicate-issues/",
        DuplicateIssueDetectionView.as_view(),
        name="ai-detect-duplicate-issues",
    ),
]
