import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-not-for-production")
os.environ.setdefault("GEOCODER_USER_AGENT", "safe-route-tests/1.0")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver")
