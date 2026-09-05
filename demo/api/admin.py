from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================
# Remove Django's default User admin registration
# ============================================================

admin.site.unregister(User)


# ============================================================
# Import custom admin registrations
# ============================================================

from . import (
    credential_admin,  # noqa: F401
    user_admin,  # noqa: F401
)
