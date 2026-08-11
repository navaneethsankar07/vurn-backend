from django.urls import path

from apps.organizations.views import (
    CreateOrganizationView,
    OrganizationOptionsView,
)

urlpatterns = [
    path(
        "",
        CreateOrganizationView.as_view(),
        name="create-organization",
    ),
    path(
        "options/",
        OrganizationOptionsView.as_view(),
        name="organization-options",
    ),
]
