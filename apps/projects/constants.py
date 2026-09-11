PROJECT_ICONS = (
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


PROJECT_STATUS_CHOICES = (
    ("active", "Active"),
    ("completed", "Completed"),
    ("archived", "Archived"),
)


PROJECT_CREATE_PERMISSION = "project.create"

PROJECT_LIST_SORT_OPTIONS = (
    "recently_created",
    "recently_updated",
    "name_asc",
    "name_desc",
)

PROJECT_ARCHIVE_FILTERS = ("all", "active", "archived")

CLOUDINARY_PROJECTS_FOLDER = "vurn/projects"

PROJECT_DELETE_CONFIRMATION_PREFIX = "DELETE"

PROJECT_MEMBER_SORT_OPTIONS = ("name_asc", "name_desc", "recently_added")


STATUS_CATEGORY_CHOICES = (
    ("backlog", "Backlog"),
    ("todo", "To Do"),
    ("in_progress", "In Progress"),
    ("done", "Done"),
)
