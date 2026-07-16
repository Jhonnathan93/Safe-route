"""Isolated and fast settings for the test suite."""

from safe_route.settings import *  # noqa: F403

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
