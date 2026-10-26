from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    ORGANIZATION_INVITATION = "organization_invitation", "Organization invitation"
    PROJECT_MEMBER_ADDED = "project_member_added", "Project member added"
    ISSUE_CREATED = "issue_created", "Issue created"
    ISSUE_ASSIGNED = "issue_assigned", "Issue assigned"
    COMMENT_ADDED = "comment_added", "Comment added"
    SPRINT_CREATED = "sprint_created", "Sprint created"
    SPRINT_STARTED = "sprint_started", "Sprint started"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=40, choices=NotificationType.choices)
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    invitation = models.ForeignKey(
        "organizations.OrganizationInvitation",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    issue = models.ForeignKey(
        "projects.Issue",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )
    sprint = models.ForeignKey(
        "projects.Sprint",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "is_read", "-created_at"],
                name="idx_notif_user_read_date",
            ),
            models.Index(fields=["user", "-created_at"], name="idx_notif_user_date"),
        ]

    def __str__(self):
        return f"{self.user_id}: {self.title}"


class FCMDevice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fcm_devices"
    )
    token = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "fcm_devices"
        indexes = [
            models.Index(fields=["user", "is_active"], name="idx_fcm_user_active")
        ]

    def __str__(self):
        return f"FCM device for user {self.user_id}"
