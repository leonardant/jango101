from .settings import *

# ============================================================
# Deployment settings
# ============================================================


# ============================================================
# Core security
# ============================================================

DEBUG = False


# ============================================================
# Allowed hosts
# ============================================================

ALLOWED_HOSTS = [
    "localhost",
]


# ============================================================
# HTTPS / SSL security
# ============================================================

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True


# ============================================================
# HTTP Strict Transport Security
# ============================================================

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True


# ============================================================
# Email
# ============================================================

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "HOST": os.environ.get("EMAIL_HOST", "localhost"),
        "PORT": int(os.environ.get("EMAIL_PORT", "587")),
        "USERNAME": os.environ.get("EMAIL_HOST_USER", ""),
        "PASSWORD": os.environ.get("EMAIL_HOST_PASSWORD", ""),
        "USE_TLS": True,
    },
}
