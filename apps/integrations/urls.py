from django.urls import path

from .views import (
    GitHubConnectView,
    GitHubRepositoryListView,
    GitHubRepositoryDetailView,
    GitHubIntegrationStatusView,
    GitHubRepositoryConnectionView,
    GitHubInstallationCompleteView,
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
        "integrations/github/complete/",
        GitHubInstallationCompleteView.as_view(),
        name="github-installation-complete",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/integrations/github/repositories/<int:repository_id>/",
        GitHubRepositoryDetailView.as_view(),
        name="github-repository-detail",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/integrations/github/repositories/connect/",
        GitHubRepositoryConnectionView.as_view(),
        name="github-repository-connect",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/integrations/github/",
        GitHubIntegrationStatusView.as_view(),
        name="github-integration-status",
    ),
]
