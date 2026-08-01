from .base import BASE_DIR, DATABASES, env, get_database_config
from .base import *

env.read_env(BASE_DIR / ".env.test")

DEBUG = env.bool("DEBUG")

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}