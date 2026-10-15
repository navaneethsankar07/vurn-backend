from django.urls import path

from .views import (
    AICreditOrderView,
    AICreditPaymentVerificationView,
    AIUsageHistoryView,
    AIUsageStatisticsView,
    ReleaseNotesView,
    SprintSummaryView,
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
    path(
        "generate-sprint-summary/",
        SprintSummaryView.as_view(),
        name="ai-generate-sprint-summary",
    ),
    path(
        "generate-release-notes/",
        ReleaseNotesView.as_view(),
        name="generate-release-notes",
    ),
    path(
        "usage-statistics/",
        AIUsageStatisticsView.as_view(),
        name="ai-usage-statistics",
    ),
    path("usage-history/", AIUsageHistoryView.as_view(), name="ai-usage-history"),
    path("ai/credit-orders/", AICreditOrderView.as_view(), name="ai-credit-order"),
    path(
        "ai/verify-credit-payment/",
        AICreditPaymentVerificationView.as_view(),
        name="ai-credit-payment-verification",
    ),
]
