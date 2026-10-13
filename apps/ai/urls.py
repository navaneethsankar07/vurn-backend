from django.urls import path

from apps.ai.views import TaskBreakdownView

urlpatterns = [
    path("task-breakdown/", TaskBreakdownView.as_view(), name="ai-task-breakdown")
]
