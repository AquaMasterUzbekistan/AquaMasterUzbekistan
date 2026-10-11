"""Security utilities."""

from __future__ import annotations

from app.config.settings import settings
from app.models.user import RoleName


def is_super_admin(telegram_id: int) -> bool:
    """Check if telegram_id is in the SUPER_ADMIN_IDS list."""
    return telegram_id in settings.SUPER_ADMIN_IDS


def is_admin(telegram_id: int) -> bool:
    """Check if telegram_id is in ADMIN_IDS or SUPER_ADMIN_IDS list."""
    admin_ids = set(getattr(settings, "ADMIN_IDS", [])) | set(getattr(settings, "SUPER_ADMIN_IDS", []))
    return telegram_id in admin_ids


def has_admin_access(role: RoleName | str) -> bool:
    """Check if role has admin panel access."""
    val = role.value if hasattr(role, "value") else str(role)
    return val in (
        RoleName.SUPER_ADMIN.value,
        RoleName.ADMIN.value,
        RoleName.EDITOR.value,
        RoleName.MODERATOR.value,
        "superadmin",
        "super_admin",
        "admin",
        "editor",
        "moderator",
    )


def has_edit_access(role: RoleName) -> bool:
    """Check if role can edit species/articles."""
    return role in (RoleName.SUPER_ADMIN, RoleName.ADMIN, RoleName.EDITOR)


def has_delete_access(role: RoleName) -> bool:
    """Only super_admin and admin can delete."""
    return role in (RoleName.SUPER_ADMIN, RoleName.ADMIN)
