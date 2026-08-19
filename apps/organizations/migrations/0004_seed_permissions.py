from django.db import migrations

PERMISSIONS = [
    {
        "code": "organization.view",
        "name": "View Organization",
        "permission_group": "organization",
        "description": "View organization information.",
    },
    {
        "code": "organization.settings.update",
        "name": "Edit Settings",
        "permission_group": "organization",
        "description": "Update organization settings.",
    },
    {
        "code": "organization.billing.manage",
        "name": "Manage Billing",
        "permission_group": "organization",
        "description": "Manage organization billing.",
    },
    {
        "code": "project.view",
        "name": "View Projects",
        "permission_group": "projects",
        "description": "View organization projects.",
    },
    {
        "code": "project.create",
        "name": "Create Projects",
        "permission_group": "projects",
        "description": "Create new projects.",
    },
    {
        "code": "project.update",
        "name": "Edit Projects",
        "permission_group": "projects",
        "description": "Update existing projects.",
    },
    {
        "code": "project.delete",
        "name": "Delete Projects",
        "permission_group": "projects",
        "description": "Delete projects.",
    },
    {
        "code": "member.view",
        "name": "View Members",
        "permission_group": "members",
        "description": "View organization members.",
    },
    {
        "code": "member.invite",
        "name": "Invite Members",
        "permission_group": "members",
        "description": "Invite users to the organization.",
    },
    {
        "code": "member.manage",
        "name": "Manage Members",
        "permission_group": "members",
        "description": "Manage organization members.",
    },
    {
        "code": "member.remove",
        "name": "Remove Members",
        "permission_group": "members",
        "description": "Remove members from the organization.",
    },
    {
        "code": "issue.view",
        "name": "View Issues",
        "permission_group": "issues",
        "description": "View project issues.",
    },
    {
        "code": "issue.create",
        "name": "Create Issues",
        "permission_group": "issues",
        "description": "Create new issues.",
    },
    {
        "code": "issue.update",
        "name": "Edit Issues",
        "permission_group": "issues",
        "description": "Update existing issues.",
    },
    {
        "code": "issue.delete",
        "name": "Delete Issues",
        "permission_group": "issues",
        "description": "Delete issues.",
    },
    {
        "code": "sprint.view",
        "name": "View Sprints",
        "permission_group": "sprints",
        "description": "View project sprints.",
    },
    {
        "code": "sprint.create",
        "name": "Create Sprints",
        "permission_group": "sprints",
        "description": "Create new sprints.",
    },
    {
        "code": "sprint.manage",
        "name": "Manage Sprints",
        "permission_group": "sprints",
        "description": "Manage sprint configuration and lifecycle.",
    },
    {
        "code": "workflow.view",
        "name": "View Workflow",
        "permission_group": "workflow",
        "description": "View project workflow.",
    },
    {
        "code": "workflow.manage",
        "name": "Manage Workflow",
        "permission_group": "workflow",
        "description": "Manage project workflow.",
    },
    {
        "code": "knowledge_base.view",
        "name": "View Docs",
        "permission_group": "knowledge_base",
        "description": "View knowledge base documents.",
    },
    {
        "code": "knowledge_base.edit",
        "name": "Edit Docs",
        "permission_group": "knowledge_base",
        "description": "Create and edit knowledge base documents.",
    },
]


def seed_permissions(apps, schema_editor):
    Permission = apps.get_model("organizations", "Permission")

    Permission.objects.bulk_create(
        [Permission(**permission) for permission in PERMISSIONS],
        ignore_conflicts=True,
    )


def remove_permissions(apps, schema_editor):
    Permission = apps.get_model("organizations", "Permission")

    Permission.objects.filter(
        code__in=[permission["code"] for permission in PERMISSIONS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0003_permission_organizationrole_and_more"),
    ]

    operations = [
        migrations.RunPython(
            seed_permissions,
            remove_permissions,
        ),
    ]
