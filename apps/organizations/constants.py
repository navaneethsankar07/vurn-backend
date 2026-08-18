ORGANIZATION_ICONS = (
    "hexagon",
    "building-2",
    "briefcase-business",
    "blocks",
    "box",
    "code-2",
    "command",
    "database",
    "globe-2",
    "layers-2",
    "layout-dashboard",
    "network",
    "panels-top-left",
    "rocket",
    "server",
    "shield-check",
    "workflow",
    "zap",
)

ORGANIZATION_ACCENT_COLORS = {
    "amber": "#F59E0B",
    "blue": "#2563EB",
    "emerald": "#059669",
    "purple": "#7C3AED",
    "red": "#FF0037",
    "lime": "#65A30D",
    "coral": "#EA580C",
    "slate": "#64748B",
    "indigo": "#4F46E5",
    "sky": "#5EE4FF",
}

LOGO_ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
LOGO_MAX_SIZE = 5 * 1024 * 1024

ORGANIZATION_DELETE_OTP_PREFIX = "organization_delete_otp"

# Temporary data until organization members and projects are implemented.
MOCK_ORGANIZATION_STATS = {
    1: {
        "member_count": 42,
        "project_count": 18,
    },
    2: {
        "member_count": 15,
        "project_count": 6,
    },
    3: {
        "member_count": 9,
        "project_count": 4,
    },
}

ORGANIZATION_SORT_FIELDS = {
    "name",
    "member",
    "project",
    "recent",
}

ORGANIZATION_SORT_ORDERS = {
    "asc",
    "desc",
}

MOCK_ORGANIZATION_DASHBOARD_STATS = {
    "total_projects": 8,
    "total_members": 12,
    "active_sprints": 2,
    "open_issues": 24,
    "completed_issues": 67,
}

ORGANIZATION_PREFERENCE_DEFAULTS = {
    "allow_admin_invitations": True,
    "allow_member_invitations": False,
    "allow_member_project_creation": False,
}


ORGANIZATION_PREFERENCE_FIELDS = (
    "allow_admin_invitations",
    "allow_member_invitations",
    "allow_member_project_creation",
)
