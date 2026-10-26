from django.urls import path

from apps.recent_activities.views import RecentActivityView

urlpatterns = [path("", RecentActivityView.as_view(), name="recent-activities")]
