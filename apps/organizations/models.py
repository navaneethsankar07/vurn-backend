from django.conf import settings
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        max_length=500,
        blank=True,
    )

    slug = models.SlugField(
        max_length=63,
        unique=True,
        db_index=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
    )

    icon = models.CharField(
        max_length=100,
        default="hexagon",
    )

    accent_color = models.CharField(
        max_length=20,
        default="amber",
    )

    logo_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    is_archived = models.BooleanField(
        default=False,
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
        db_table = "organizations"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["slug"],
                name="idx_organization_slug",
            ),
            models.Index(
                fields=["deleted_at"],
                name="idx_organization_deleted_at",
            ),
            models.Index(
                fields=["deleted_at", "is_archived"],
                name="idx_organization_status",
            ),
        ]

    def __str__(self):
        return self.name


class OrganizationPreference(models.Model):
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="preferences",
    )

    allow_admin_invitations = models.BooleanField(
        default=True,
    )

    allow_member_invitations = models.BooleanField(
        default=False,
    )

    allow_member_project_creation = models.BooleanField(
        default=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Preferences for {self.organization.name}"
