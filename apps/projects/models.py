from django.conf import settings
from django.db import models
from django.utils import timezone

from .constants import PROJECT_STATUS_CHOICES


class Project(models.Model):

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="projects",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects",
    )

    project_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="led_projects",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_projects",
    )

    name = models.CharField(
        max_length=150,
    )

    key = models.CharField(
        max_length=10,
    )

    slug = models.SlugField(
        max_length=180,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.CharField(
        max_length=100,
        default="hexagon",
    )

    accent_color = models.CharField(
        max_length=7,
        default="#F59E0B",
    )

    logo_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default="active",
    )

    is_archived = models.BooleanField(
        default=False,
    )

    start_date = models.DateField(
        blank=True,
        null=True,
    )

    target_date = models.DateField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    class Meta:

        db_table = "projects"

        ordering = [
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "organization",
                    "key",
                ),
                name="uq_project_key_per_org",
            ),
            models.UniqueConstraint(
                fields=(
                    "organization",
                    "slug",
                ),
                name="uq_project_slug_per_org",
            ),
        ]

        indexes = [
            models.Index(
                fields=["deleted_at"],
                name="idx_projects_deleted_at",
            ),
            models.Index(
                fields=[
                    "organization",
                    "is_archived",
                    "deleted_at",
                ],
                name="idx_projects_org_archived",
            ),
        ]

    def __str__(self):
        return f"{self.key} - {self.name}"
