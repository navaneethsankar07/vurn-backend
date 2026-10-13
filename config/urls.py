from django.urls import include, path

urlpatterns = [
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/profile/", include("apps.profiles.urls")),
    path("api/v1/organizations/", include("apps.organizations.urls")),
    path("api/v1/projects/", include("apps.projects.urls")),
    path("api/v1/", include("apps.integrations.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/search/", include("apps.search.urls")),
    path("api/v1/help/", include("apps.help_center.urls")),
]
