from django.urls import path

from .views import (
    ProjectArchiveView,
    ProjectDeleteView,
    ProjectMemberView,
    ProjectOptionsView,
    ProjectSettingsView,
    ProjectView,
    ProjectWorkflowView,
    WorkflowStatusView,
)

urlpatterns = [
    path("", ProjectView.as_view(), name="projects"),
    path("options/", ProjectOptionsView.as_view(), name="project-options"),
    path(
        "<slug:project_slug>/settings/",
        ProjectSettingsView.as_view(),
        name="project-settings",
    ),
    path(
        "<slug:project_slug>/archive/",
        ProjectArchiveView.as_view(),
        name="project-archive",
    ),
    path(
        "<slug:project_slug>/members/",
        ProjectMemberView.as_view(),
        name="project-members",
    ),
    path(
        "<slug:project_slug>/members/<int:user_id>/",
        ProjectMemberView.as_view(),
        name="project-member",
    ),
    path("<slug:project_slug>/", ProjectDeleteView.as_view(), name="project-delete"),
    path(
        "<slug:project_slug>/workflow/",
        ProjectWorkflowView.as_view(),
        name="project-workflow",
    ),
    path(
        "<slug:project_slug>/workflow/statuses/",
        WorkflowStatusView.as_view(),
        name="workflow-statuses",
    ),
]
