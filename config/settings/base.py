from pathlib import Path
import environ
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env.read_env(BASE_DIR / ".env.development")

# -----------------------------------------------------------------------------
# Django Core
# -----------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-Party Apps
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # Local Apps
    "apps.accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------


def get_database_config():
    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DATABASE_NAME"),
            "USER": env("DATABASE_USER"),
            "PASSWORD": env("DATABASE_PASSWORD"),
            "HOST": env("DATABASE_HOST"),
            "PORT": env("DATABASE_PORT"),
        }
    }


# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# -----------------------------------------------------------------------------
# Static Files
# -----------------------------------------------------------------------------

STATIC_URL = "static/"

# -----------------------------------------------------------------------------
# Django REST Framework
# -----------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# -----------------------------------------------------------------------------
# Email Configuration
# -----------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")

# -----------------------------------------------------------------------------
# OTP Configuration
# -----------------------------------------------------------------------------
OTP_LENGTH = 6
OTP_EXPIRATION_SECONDS = 300

#  -----------------------------------------------------------------------------
# Google Client Configuration
# -----------------------------------------------------------------------------GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")

#  -----------------------------------------------------------------------------
# Password Reset Configuration
# -----------------------------------------------------------------------------GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
PASSWORD_RESET_EXPIRATION_SECONDS = env.int(
    "PASSWORD_RESET_EXPIRATION_SECONDS",
    default=600,
)

FRONTEND_URL = env("FRONTEND_URL")
