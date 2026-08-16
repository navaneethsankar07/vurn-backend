from django.urls import path

from .views import (
    OrganizationBrandingView,
    OrganizationDashboardView,
    OrganizationOptionsView,
    OrganizationSettingsView,
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
    path(
        "<slug:slug>/settings/",
        OrganizationSettingsView.as_view(),
        name="organization-settings",
    ),
    path(
        "<slug:slug>/branding/",
        OrganizationBrandingView.as_view(),
        name="organization-branding",
    ),
]
