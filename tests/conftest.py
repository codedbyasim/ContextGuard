import os

# Keep existing API tests working without bearer tokens.
os.environ.setdefault("AUTH_DISABLED", "true")
