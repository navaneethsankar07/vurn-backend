from django.urls import path

from .views import (
    ProjectOptionsView,
    ProjectSettingsView,
    ProjectView,
)

urlpatterns = [
    path(
        "",
        ProjectView.as_view(),
        name="projects",
    ),
    path(
        "options/",
        ProjectOptionsView.as_view(),
        name="project-options",
    ),
    path(
        "<slug:project_slug>/settings/",
        ProjectSettingsView.as_view(),
        name="project-settings",
    ),
]
