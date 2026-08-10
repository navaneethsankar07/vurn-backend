from django.urls import include, path

urlpatterns = [
    path("api/v1/auth/", include("apps.accounts.urls")),
    path(
        "api/v1/profile/",
        include("apps.profiles.urls"),
    ),
]
