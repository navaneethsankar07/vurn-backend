from django.urls import path

from apps.organizations.views import (
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
]
