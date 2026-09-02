from django.urls import path

from .views import (
    ProjectOptionsView,
)

urlpatterns = [
    path(
        "options/",
        ProjectOptionsView.as_view(),
        name="project-options",
    ),
]
