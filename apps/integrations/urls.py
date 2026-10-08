from django.urls import path

from .views import (
    GitHubConnectView,
    GitHubInstallationCallbackView,
    GitHubRepositoryListView,
)

urlpatterns = [
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/integrations/github/connect/",
        GitHubConnectView.as_view(),
        name="github-connect",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/integrations/github/repositories/",
        GitHubRepositoryListView.as_view(),
        name="github-repositories",
    ),
    path(
        "integrations/github/callback/",
        GitHubInstallationCallbackView.as_view(),
        name="github-installation-callback",
    ),
]
