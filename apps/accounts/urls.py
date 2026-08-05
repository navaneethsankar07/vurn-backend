from django.urls import path
from .views import LoginView, LogoutView, RefreshTokenView, SendOTPView, RegisterView

urlpatterns = [
    path(
        "send-otp/",
        SendOTPView.as_view(),
        name="send-otp",
    ),
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "refresh/",
        RefreshTokenView.as_view(),
        name="refresh-token",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
]
