from django.conf import settings
from django.db import models
from django.utils import timezone

from .constants import PROJECT_STATUS_CHOICES, STATUS_CATEGORY_CHOICES


class Project(models.Model):

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="projects"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects",
    )
    project_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="led_projects"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_projects",
    )
    name = models.CharField(max_length=150)
    key = models.CharField(max_length=10)
    slug = models.SlugField(max_length=180)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, default="hexagon")
    accent_color = models.CharField(max_length=7, default="#F59E0B")
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=PROJECT_STATUS_CHOICES, default="active"
    )
    is_archived = models.BooleanField(default=False)
    start_date = models.DateField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:

        db_table = "projects"

        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=("organization", "key"),
                name="uq_project_key_per_org",
            ),
            models.UniqueConstraint(
                fields=("organization", "slug"),
                name="uq_project_slug_per_org",
            ),
        ]

        indexes = [
            models.Index(
                fields=["deleted_at"],
                name="idx_projects_deleted_at",
            ),
            models.Index(
                fields=["organization", "is_archived", "deleted_at"],
                name="idx_projects_org_archived",
            ),
        ]

    def __str__(self):
        return f"{self.key} - {self.name}"


class ProjectMember(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    project_role = models.CharField(max_length=100)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "project_members"
        constraints = [
            models.UniqueConstraint(
                fields=("project", "user"), name="uq_project_member"
            ),
        ]
        indexes = [
            models.Index(fields=("project",), name="idx_project_members_project"),
            models.Index(fields=("user",), name="idx_project_members_user"),
        ]

    def __str__(self):
        return f"{self.user.email} - " f"{self.project.name}"


class WorkflowStatus(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="workflow_statuses"
    )
    name = models.CharField(max_length=60)
    category = models.CharField(max_length=20, choices=STATUS_CATEGORY_CHOICES)
    color = models.CharField(max_length=7)
    icon = models.CharField(max_length=50, blank=True, null=True)
    position = models.PositiveIntegerField()
    is_default = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    allow_from_backlog = models.BooleanField(default=True)
    allow_incoming = models.BooleanField(default=True)
    allow_outgoing = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "workflow_statuses"
        constraints = [
            models.UniqueConstraint(
                fields=("project", "name"), name="uq_status_name_per_project"
            ),
        ]
        indexes = [
            models.Index(fields=("project",), name="idx_workflow_status_project"),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class WorkflowTransition(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="workflow_transitions",
    )
    from_status = models.ForeignKey(
        "WorkflowStatus", on_delete=models.CASCADE, related_name="outgoing_transitions"
    )
    to_status = models.ForeignKey(
        "WorkflowStatus", on_delete=models.CASCADE, related_name="incoming_transitions"
    )
    name = models.CharField(max_length=60, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "workflow_transitions"
        constraints = [
            models.UniqueConstraint(
                fields=("project", "from_status", "to_status"),
                name="uq_workflow_transition",
            ),
        ]
        indexes = [
            models.Index(fields=("project",), name="idx_workflow_transition_project"),
        ]

    def __str__(self):
        return f"{self.from_status.name} → " f"{self.to_status.name}"
