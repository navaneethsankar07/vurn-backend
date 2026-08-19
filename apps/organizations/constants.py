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


ORGANIZATION_PERMISSIONS = {
    "organization": [
        {
            "code": "organization.view",
            "name": "View Organization",
            "description": "View organization information.",
        },
        {
            "code": "organization.settings.update",
            "name": "Edit Settings",
            "description": "Update organization settings.",
        },
        {
            "code": "organization.billing.manage",
            "name": "Manage Billing",
            "description": "Manage organization billing.",
        },
    ],
    "projects": [
        {
            "code": "project.view",
            "name": "View Projects",
            "description": "View organization projects.",
        },
        {
            "code": "project.create",
            "name": "Create Projects",
            "description": "Create new projects.",
        },
        {
            "code": "project.update",
            "name": "Edit Projects",
            "description": "Update existing projects.",
        },
        {
            "code": "project.delete",
            "name": "Delete Projects",
            "description": "Delete projects.",
        },
    ],
    "members": [
        {
            "code": "member.view",
            "name": "View Members",
            "description": "View organization members.",
        },
        {
            "code": "member.invite",
            "name": "Invite Members",
            "description": "Invite users to the organization.",
        },
        {
            "code": "member.manage",
            "name": "Manage Members",
            "description": "Manage organization member details and roles.",
        },
        {
            "code": "member.remove",
            "name": "Remove Members",
            "description": "Remove members from the organization.",
        },
    ],
    "issues": [
        {
            "code": "issue.view",
            "name": "View Issues",
            "description": "View project issues.",
        },
        {
            "code": "issue.create",
            "name": "Create Issues",
            "description": "Create new issues.",
        },
        {
            "code": "issue.update",
            "name": "Edit Issues",
            "description": "Update existing issues.",
        },
        {
            "code": "issue.delete",
            "name": "Delete Issues",
            "description": "Delete issues.",
        },
    ],
    "sprints": [
        {
            "code": "sprint.view",
            "name": "View Sprints",
            "description": "View project sprints.",
        },
        {
            "code": "sprint.create",
            "name": "Create Sprints",
            "description": "Create new sprints.",
        },
        {
            "code": "sprint.manage",
            "name": "Manage Sprints",
            "description": "Manage sprint configuration and lifecycle.",
        },
    ],
    "workflow": [
        {
            "code": "workflow.view",
            "name": "View Workflow",
            "description": "View project workflow configuration.",
        },
        {
            "code": "workflow.manage",
            "name": "Manage Workflow",
            "description": "Manage project workflow configuration.",
        },
    ],
    "knowledge_base": [
        {
            "code": "knowledge_base.view",
            "name": "View Docs",
            "description": "View knowledge base documents.",
        },
        {
            "code": "knowledge_base.edit",
            "name": "Edit Docs",
            "description": "Create and edit knowledge base documents.",
        },
    ],
}


ORGANIZATION_ROLE_NAME_MAX_LENGTH = 50
ORGANIZATION_ROLE_COLOR_MAX_LENGTH = 7


ORGANIZATION_ROLE_SORT_FIELDS = {
    "name": "name",
    "created": "created_at",
    "updated": "updated_at",
}

ORGANIZATION_ROLE_SORT_ORDERS = {
    "asc": "",
    "desc": "-",
}
