import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .constants import ORGANIZATION_ROLE_CHOICES


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


class Permission(models.Model):
    code = models.CharField(
        max_length=100,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    permission_group = models.CharField(
        max_length=50,
    )

    description = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.name


class OrganizationRole(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="roles",
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    color = models.CharField(
        max_length=7,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="uq_organization_role_name",
            ),
        ]

    def __str__(self):
        return self.name


class OrganizationRolePermission(models.Model):
    role = models.ForeignKey(
        OrganizationRole,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="uq_organization_role_permission",
            ),
        ]


class OrganizationMember(models.Model):
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=ORGANIZATION_ROLE_CHOICES,
        default="member",
    )

    job_role = models.ForeignKey(
        "OrganizationRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="invited_organization_members",
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "organization_members"

        constraints = [
            models.UniqueConstraint(
                fields=("organization", "user"),
                name="uq_org_member",
            ),
        ]


class OrganizationInvitation(models.Model):
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.CASCADE,
        related_name="invitations",
    )

    email = models.EmailField()

    personal_message = models.TextField(
        blank=True,
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    permission_role = models.CharField(
        max_length=20,
        choices=ORGANIZATION_ROLE_CHOICES,
        default="member",
    )

    job_role = models.ForeignKey(
        "OrganizationRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations",
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_invitations_sent",
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "organization_invitations"

        indexes = [
            models.Index(fields=("organization",)),
            models.Index(fields=("email",)),
            models.Index(fields=("expires_at",)),
        ]
