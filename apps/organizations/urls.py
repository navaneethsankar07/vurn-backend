from django.urls import path

from apps.organizations.views import (
    CreateOrganizationView,
)

urlpatterns = [
    path(
        "",
        CreateOrganizationView.as_view(),
        name="create-organization",
    ),
]
