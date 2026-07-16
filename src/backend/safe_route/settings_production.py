"""Settings for deployment processes."""

import os

from safe_route.settings import *  # noqa: F403

DEBUG = False
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "true").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
