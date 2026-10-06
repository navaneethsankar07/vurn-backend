from django.conf import settings
from django.db import models
from django.utils import timezone

from .constants import (
    COMMENT_REACTION_CHOICES,
    ISSUE_PRIORITY_CHOICES,
    ISSUE_TYPE_CHOICES,
    PROJECT_STATUS_CHOICES,
    SPRINT_STATUS_CHOICES,
    STATUS_CATEGORY_CHOICES,
)


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
        return f"{self.user.email} - " f"{self.project.name} - " f"{self.user.id}"


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
            models.Index(fields=("project",), name="idx_wf_transition_project"),
        ]

    def __str__(self):
        return f"{self.from_status.name} → " f"{self.to_status.name}"


class Sprint(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="sprints"
    )
    name = models.CharField(max_length=150)
    goal = models.TextField(blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    estimated_days = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=SPRINT_STATUS_CHOICES, default="planned"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_sprints",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sprints"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("project", "name"), name="uq_sprint_name_per_project"
            )
        ]
        indexes = [
            models.Index(fields=["project"], name="idx_sprints_project"),
            models.Index(fields=["status"], name="idx_sprints_status"),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Issue(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="issues"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", null=True, blank=True
    )
    labels = models.ManyToManyField(
        "projects.Label", through="IssueLabel", related_name="issues", blank=True
    )
    sprint = models.ForeignKey(
        "projects.Sprint",
        on_delete=models.SET_NULL,
        related_name="issues",
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        "projects.WorkflowStatus", on_delete=models.PROTECT, related_name="issues"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_issues",
        null=True,
        blank=True,
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_issues",
    )
    issue_number = models.PositiveIntegerField()
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=20, choices=ISSUE_PRIORITY_CHOICES, default="medium"
    )
    story_points = models.PositiveIntegerField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    estimated_time = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "issues"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("project", "issue_number"), name="uq_issue_number_per_project"
            )
        ]
        indexes = [
            models.Index(fields=("project",), name="idx_issues_project"),
            models.Index(
                fields=("project", "issue_type"), name="idx_issues_project_type"
            ),
            models.Index(
                fields=("project", "status"), name="idx_issues_project_status"
            ),
            models.Index(
                fields=("project", "sprint"), name="idx_issues_project_sprint"
            ),
            models.Index(fields=("parent",), name="idx_issues_parent"),
            models.Index(fields=("assignee",), name="idx_issues_assignee"),
            models.Index(fields=("deleted_at",), name="idx_issues_deleted_at"),
        ]

    @property
    def key(self):
        return f"{self.project.key}-{self.issue_number}"

    def __str__(self):
        return f"{self.key} - {self.title}"


class IssueSprintHistory(models.Model):
    issue = models.ForeignKey(
        "projects.Issue", on_delete=models.CASCADE, related_name="sprint_history"
    )
    sprint = models.ForeignKey(
        "projects.Sprint",
        on_delete=models.PROTECT,
        related_name="issue_sprint_history",
        null=True,
        blank=True,
    )
    moved_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "issue_sprint_history"
        ordering = ["moved_at"]
        indexes = [
            models.Index(fields=("issue", "moved_at"), name="idx_issue_sprint_history"),
            models.Index(fields=("sprint",), name="idx_sprint_issue_history"),
        ]


class Label(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="labels"
    )
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#999999")

    class Meta:
        db_table = "labels"
        constraints = [
            models.UniqueConstraint(
                fields=("project", "name"), name="uq_label_per_project"
            )
        ]
        indexes = [models.Index(fields=("project",), name="idx_labels_project")]

    def __str__(self):
        return self.name


class IssueLabel(models.Model):
    issue = models.ForeignKey(
        "projects.Issue", on_delete=models.CASCADE, related_name="issue_labels"
    )
    label = models.ForeignKey(
        "projects.Label", on_delete=models.CASCADE, related_name="issue_labels"
    )

    class Meta:
        db_table = "issue_labels"
        constraints = [
            models.UniqueConstraint(fields=("issue", "label"), name="uq_issue_label")
        ]
        indexes = [
            models.Index(fields=("issue",), name="idx_issue_labels_issue"),
            models.Index(fields=("label",), name="idx_issue_labels_label"),
        ]


class Comment(models.Model):
    issue = models.ForeignKey(
        "projects.Issue", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["issue"], name="idx_comments_issue"),
            models.Index(fields=["parent"], name="idx_comments_parent"),
        ]

    def __str__(self):
        return f"{self.author} - {self.issue.key}"


class CommentReaction(models.Model):
    comment = models.ForeignKey(
        "projects.Comment", on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_reactions",
    )
    reaction = models.CharField(max_length=20, choices=COMMENT_REACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comment_reactions"
        constraints = [
            models.UniqueConstraint(
                fields=("comment", "user"), name="uq_comment_reaction_user"
            )
        ]
        indexes = [
            models.Index(fields=("comment",), name="idx_comment_reactions_comment")
        ]


class Attachment(models.Model):
    issue = models.ForeignKey(
        "projects.Issue",
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
    )
    document = models.ForeignKey(
        "projects.Document",
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_attachments",
    )
    file_name = models.CharField(max_length=255)
    object_key = models.CharField(max_length=500)
    file_size = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "attachments"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(issue__isnull=False) | models.Q(document__isnull=False)
                ),
                name="attachment_has_parent",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(issue__isnull=True) | models.Q(document__isnull=True)
                ),
                name="attachment_single_parent",
            ),
            models.UniqueConstraint(
                fields=("issue", "object_key"), name="uq_attachment_issue_object_key"
            ),
            models.UniqueConstraint(
                fields=("document", "object_key"),
                name="uq_attachment_document_object_key",
            ),
        ]
        indexes = [
            models.Index(fields=("issue",), name="idx_attachments_issue"),
            models.Index(fields=("document",), name="idx_attachments_document"),
            models.Index(fields=("uploaded_by",), name="idx_attachments_uploaded_by"),
        ]

    def __str__(self):
        return self.file_name


class DocumentFolder(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="document_folders"
    )
    name = models.CharField(max_length=150)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_document_folders",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "document_folders"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("project", "name"), name="uq_document_folder_project_name"
            )
        ]
        indexes = [
            models.Index(fields=("project",), name="idx_document_folders_project")
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Document(models.Model):
    folder = models.ForeignKey(
        "projects.DocumentFolder", on_delete=models.PROTECT, related_name="documents"
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_documents",
    )
    current_version = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "documents"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=("folder",), name="idx_documents_folder"),
            models.Index(fields=("project",), name="idx_documents_project"),
            models.Index(fields=("deleted_at",), name="idx_documents_deleted_at"),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.title}"


class ProjectTag(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="tags"
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "project_tags"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("project", "name"), name="uq_project_tag_name"
            )
        ]
        indexes = [models.Index(fields=("project",), name="idx_project_tags_project")]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class DocumentTag(models.Model):
    document = models.ForeignKey(
        "projects.Document", on_delete=models.CASCADE, related_name="document_tags"
    )
    tag = models.ForeignKey(
        "projects.ProjectTag", on_delete=models.CASCADE, related_name="document_tags"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "document_tags"
        constraints = [
            models.UniqueConstraint(fields=("document", "tag"), name="uq_document_tag")
        ]
        indexes = [
            models.Index(fields=("document",), name="idx_document_tags_document"),
            models.Index(fields=("tag",), name="idx_document_tags_tag"),
            models.Index(fields=("created_at",), name="idx_document_tags_created_at"),
        ]
