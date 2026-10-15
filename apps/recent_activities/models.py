from django.conf import settings
from django.db import models


class RecentActivity(models.Model):
    class ActivityType(models.TextChoices):
        ORGANIZATION_CREATED = "organization_created", "Organization Created"
        PROJECT_CREATED = "project_created", "Project Created"
        ISSUE_CREATED = "issue_created", "Issue Created"
        INVITATION_ACCEPTED = "invitation_accepted", "Invitation Accepted"
        SPRINT_CREATED = "sprint_created", "Sprint Created"
        ISSUE_UPDATED = "issue_updated", "Issue Updated"
        ISSUE_COMPLETED = "issue_completed", "Issue Completed"

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="recent_activities",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recent_activities",
    )
    sprint = models.ForeignKey(
        "projects.Sprint",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recent_activities",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recent_activities",
    )
    activity_type = models.CharField(max_length=40, choices=ActivityType.choices)
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recent_activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["organization", "-created_at"], name="idx_activity_org_created"
            ),
            models.Index(
                fields=["project", "-created_at"], name="idx_activity_project_created"
            ),
            models.Index(
                fields=["sprint", "-created_at"], name="idx_activity_sprint_created"
            ),
        ]

    def __str__(self):
        return f"{self.activity_type}: {self.description}"
