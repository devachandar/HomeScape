"""
Django settings for the Inquiry Service.
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-secret-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "inquiries",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = []
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get(
            "DATABASE_URL",
            "postgres://homescape:homescape@postgres:5432/inquiry_db",
        )
    )
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "inquiries.jwt_auth.StatelessJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "inquiries.exceptions.friendly_exception_handler",
}

JWT_ACCESS_SECRET = os.environ.get("JWT_ACCESS_SECRET", "dev-only-jwt-secret-change-me")
JWT_ACCESS_TTL_MINUTES = int(os.environ.get("JWT_ACCESS_TTL_MINUTES", "15"))
JWT_REFRESH_TTL_DAYS = int(os.environ.get("JWT_REFRESH_TTL_DAYS", "7"))

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

INTERNAL_SERVICE_URLS = {
    "auth": os.environ.get("AUTH_SERVICE_URL", "http://auth-service:4001"),
    "property": os.environ.get("PROPERTY_SERVICE_URL", "http://property-service:4002"),
    "search": os.environ.get("SEARCH_SERVICE_URL", "http://search-service:4003"),
    "inquiry": os.environ.get("INQUIRY_SERVICE_URL", "http://inquiry-service:4004"),
    "media": os.environ.get("MEDIA_SERVICE_URL", "http://media-service:4005"),
}
