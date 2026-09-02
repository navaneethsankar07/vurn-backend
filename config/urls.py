from django.urls import include, path

urlpatterns = [
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/profile/", include("apps.profiles.urls")),
    path("api/v1/organizations/", include("apps.organizations.urls")),
    path("api/v1/projects/", include("apps.projects.urls")),
]
