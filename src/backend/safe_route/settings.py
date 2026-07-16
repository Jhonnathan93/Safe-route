import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("The DJANGO_SECRET_KEY environment variable is required.")

DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if host]
INSTALLED_APPS = [
    "django.contrib.contenttypes", "django.contrib.staticfiles", "corsheaders",
    "rest_framework", "routing.apps.RoutingConfig",
]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", "django.middleware.common.CommonMiddleware"]
ROOT_URLCONF = "safe_route.urls"
TEMPLATES = []
WSGI_APPLICATION = "safe_route.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("DJANGO_DATABASE_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Bogota"
USE_TZ = True
STATIC_URL = "static/"
CORS_ALLOWED_ORIGINS = [origin for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
}
DATASET_PATH = os.getenv("DATASET_PATH", str(BASE_DIR / "data/calles_de_medellin_con_acoso.csv"))
GEOCODER_USER_AGENT = os.environ["GEOCODER_USER_AGENT"]
GEOCODER_TIMEOUT_SECONDS = float(os.getenv("GEOCODER_TIMEOUT_SECONDS", "8"))
