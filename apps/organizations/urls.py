from django.urls import path

from .views import (
    OrganizationDashboardView,
    OrganizationOptionsView,
    OrganizationView,
)

urlpatterns = [
    path(
        "",
        OrganizationView.as_view(),
        name="organization",
    ),
    path(
        "options/",
        OrganizationOptionsView.as_view(),
        name="organization-options",
    ),
    path(
        "<slug:slug>/dashboard/",
        OrganizationDashboardView.as_view(),
        name="organization-dashboard",
    ),
]
