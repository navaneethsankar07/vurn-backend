import re

from django.db.migrations import serializer
from rest_framework import serializers

from .models import (
    Attachment,
    Comment,
    Document,
    DocumentFolder,
    Issue,
    Label,
    Project,
    Sprint,
    WorkflowStatus,
)

from .constants import (
    ALLOWED_ATTACHMENT_MIME_TYPES,
    COMMENT_REACTION_CHOICES,
    COMMENT_SORT_CHOICES,
    ISSUE_PRIORITY_CHOICES,
    ISSUE_SORT_CHOICES,
    ISSUE_TYPE_CHOICES,
    KANBAN_SORT_CHOICES,
    MAX_ATTACHMENT_SIZE,
    PROJECT_ICONS,
    PROJECT_STATUS_CHOICES,
    SPRINT_STATUS_CHOICES,
    STATUS_CATEGORY_CHOICES,
)


class ProjectCreateSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=150)
    key = serializers.CharField(max_length=10)
    description = serializers.CharField(required=False, allow_blank=True)
    icon = serializers.ChoiceField(
        choices=PROJECT_ICONS, required=False, default="hexagon"
    )
    accent_color = serializers.CharField(
        max_length=7, required=False, default="#F59E0B"
    )
    start_date = serializers.DateField(required=False, allow_null=True)
    target_date = serializers.DateField(required=False, allow_null=True)

    def validate_name(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Project name cannot be empty.")

        return value

    def validate_key(
        self,
        value,
    ):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Project key cannot be empty.")

        if not re.fullmatch(
            r"[A-Z][A-Z0-9]*",
            value,
        ):
            raise serializers.ValidationError(
                "Project key must start with a letter and contain "
                "only uppercase letters and numbers."
            )

        return value

    def validate_accent_color(
        self,
        value,
    ):
        value = value.strip().upper()

        if not re.fullmatch(
            r"#[0-9A-F]{6}",
            value,
        ):
            raise serializers.ValidationError("Enter a valid hex color.")

        return value

    def validate(
        self,
        attrs,
    ):
        start_date = attrs.get(
            "start_date",
        )

        target_date = attrs.get(
            "target_date",
        )

        if start_date and target_date and target_date < start_date:
            raise serializers.ValidationError(
                {
                    "target_date": ("Target date cannot be before " "the start date."),
                }
            )

        return attrs


class ProjectResponseSerializer(
    serializers.Serializer,
):
    id = serializers.IntegerField()
    name = serializers.CharField()
    key = serializers.CharField()
    slug = serializers.SlugField()
    description = serializers.CharField()
    icon = serializers.CharField()
    accent_color = serializers.CharField()
    logo_url = serializers.URLField(allow_null=True)
    status = serializers.CharField()
    start_date = serializers.DateField(allow_null=True)
    target_date = serializers.DateField(allow_null=True)
    owner_id = serializers.IntegerField()
    project_lead_id = serializers.IntegerField()
    created_by_id = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class ProjectListSerializer(
    serializers.ModelSerializer,
):
    owner = serializers.SerializerMethodField()
    project_lead = serializers.SerializerMethodField()

    class Meta:
        model = Project

        fields = [
            "id",
            "name",
            "key",
            "slug",
            "description",
            "icon",
            "accent_color",
            "logo_url",
            "status",
            "start_date",
            "target_date",
            "owner",
            "project_lead",
            "created_at",
        ]

    def get_owner(
        self,
        obj,
    ):
        return {
            "id": obj.owner.id,
            "name": obj.owner.full_name,
            "email": obj.owner.email,
            "avatar": obj.owner.avatar,
        }

    def get_project_lead(
        self,
        obj,
    ):
        return {
            "id": obj.project_lead.id,
            "name": obj.project_lead.full_name,
            "email": obj.project_lead.email,
            "avatar": obj.project_lead.avatar,
        }


class ProjectUpdateSerializer(
    serializers.Serializer,
):
    name = serializers.CharField(max_length=150, required=False)

    key = serializers.CharField(max_length=10, required=False)

    description = serializers.CharField(required=False, allow_blank=True)

    status = serializers.ChoiceField(choices=PROJECT_STATUS_CHOICES, required=False)

    icon = serializers.ChoiceField(choices=PROJECT_ICONS, required=False)

    accent_color = serializers.CharField(max_length=7, required=False)

    logo = serializers.ImageField(required=False, write_only=True)

    def validate_name(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Project name cannot be empty.")

        return value

    def validate_key(
        self,
        value,
    ):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Project key cannot be empty.")

        if not re.fullmatch(
            r"[A-Z][A-Z0-9]*",
            value,
        ):
            raise serializers.ValidationError(
                "Project key must start with a letter and contain "
                "only uppercase letters and numbers."
            )

        return value

    def validate_accent_color(
        self,
        value,
    ):
        value = value.strip().upper()

        if not re.fullmatch(
            r"#[0-9A-F]{6}",
            value,
        ):
            raise serializers.ValidationError("Enter a valid hex color.")

        return value

    def validate(
        self,
        attrs,
    ):

        return attrs


class ProjectSettingsSerializer(serializers.Serializer):
    name = serializers.CharField()
    key = serializers.CharField()
    description = serializers.CharField()
    serializers.ChoiceField(choices=PROJECT_STATUS_CHOICES)
    icon = serializers.CharField()
    accent_color = serializers.CharField()
    logo_url = serializers.URLField(allow_null=True)
    created_by = serializers.CharField(source="created_by.full_name")
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class ProjectDeleteSerializer(serializers.Serializer):
    confirmation = serializers.CharField(required=True, trim_whitespace=False)


class ProjectMemberCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    project_role = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )

    def validate_project_role(self, value):
        return value.strip()


class ProjectMemberSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    user_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    avatar = serializers.URLField(allow_null=True)
    project_role = serializers.CharField()
    joined_at = serializers.DateTimeField()


class WorkflowStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStatus
        fields = [
            "id",
            "name",
            "category",
            "color",
            "icon",
            "position",
            "is_default",
            "is_archived",
            "allow_from_backlog",
            "allow_incoming",
            "allow_outgoing",
        ]


class WorkflowTransitionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    from_status_id = serializers.IntegerField()
    to_status_id = serializers.IntegerField()
    name = serializers.CharField()


class WorkflowOverviewSerializer(serializers.Serializer):
    statuses = WorkflowStatusSerializer(many=True)
    transitions = WorkflowTransitionSerializer(many=True)


class WorkflowStatusCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=60)
    category = serializers.ChoiceField(choices=STATUS_CATEGORY_CHOICES)
    color = serializers.CharField(max_length=7)
    icon = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True
    )
    position = serializers.IntegerField(min_value=0)
    is_default = serializers.BooleanField(required=False, default=False)
    allow_from_backlog = serializers.BooleanField(required=False, default=True)
    allow_incoming = serializers.BooleanField(required=False, default=True)
    allow_outgoing = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Status name cannot be empty.")

        return value

    def validate_color(self, value):
        value = value.strip().upper()

        if not re.fullmatch(r"#[0-9A-F]{6}", value):
            raise serializers.ValidationError("Enter a valid hex color.")

        return value


class WorkflowStatusUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=60, required=False)
    category = serializers.ChoiceField(choices=STATUS_CATEGORY_CHOICES, required=False)
    color = serializers.CharField(max_length=7, required=False)
    icon = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True
    )
    position = serializers.IntegerField(min_value=0, required=False)
    is_default = serializers.BooleanField(required=False)
    is_archived = serializers.BooleanField(required=False)
    allow_from_backlog = serializers.BooleanField(required=False)
    allow_incoming = serializers.BooleanField(required=False)
    allow_outgoing = serializers.BooleanField(required=False)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Status name cannot be empty.")

        return value

    def validate_color(self, value):
        value = value.strip().upper()

        if not re.fullmatch(r"#[0-9A-F]{6}", value):
            raise serializers.ValidationError("Enter a valid hex color.")

        return value


class WorkflowTransitionCreateSerializer(serializers.Serializer):
    from_status_id = serializers.IntegerField()
    to_status_id = serializers.IntegerField()
    name = serializers.CharField(max_length=60, required=False, allow_blank=True)


class WorkflowTransitionUpdateSerializer(serializers.Serializer):
    from_status_id = serializers.IntegerField()
    to_status_id = serializers.IntegerField()
    name = serializers.CharField(max_length=60, required=False, allow_blank=True)


class WorkflowStatusPositionSerializer(serializers.Serializer):
    position = serializers.IntegerField(min_value=0)


class SprintSerializer(serializers.ModelSerializer):
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = Sprint
        fields = [
            "id",
            "name",
            "goal",
            "description",
            "start_date",
            "end_date",
            "estimated_days",
            "status",
            "created_by_id",
            "created_by_name",
            "created_at",
            "updated_at",
        ]


class SprintListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=SPRINT_STATUS_CHOICES, required=False)
    sort = serializers.ChoiceField(
        choices=[
            "name_asc",
            "name_desc",
            "start_date_asc",
            "start_date_desc",
            "end_date_asc",
            "end_date_desc",
            "created_asc",
            "created_desc",
        ],
        required=False,
        default="created_desc",
    )


class SprintCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    goal = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    estimated_days = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Sprint name cannot be empty.")

        return value

    def validate(self, attrs):
        end_date = attrs.get("end_date")
        estimated_days = attrs.get("estimated_days")

        if end_date is None and estimated_days is None:
            raise serializers.ValidationError(
                "Either end date or estimated days is required."
            )

        if end_date is not None and estimated_days is not None:
            raise serializers.ValidationError(
                "Provide either end date or estimated days."
            )

        if end_date is not None:
            if attrs["start_date"] > end_date:
                raise serializers.ValidationError(
                    {"end_date": ("End date must be after the start date.")}
                )

        return attrs


class SprintUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=False)
    goal = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False, allow_null=True)
    estimated_days = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Sprint name cannot be empty.")

        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        estimated_days = attrs.get("estimated_days")

        if end_date is not None and estimated_days is not None:
            raise serializers.ValidationError(
                "Provide either end date or estimated days."
            )

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError(
                    {
                        "end_date": (
                            "End date must be after or equal " "to the start date."
                        )
                    }
                )

        return attrs


class SprintCompletionIssueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField()
    title = serializers.CharField()
    issue_type = serializers.CharField()
    status_id = serializers.IntegerField(source="status.id")
    status_name = serializers.CharField(source="status.name")
    parent_id = serializers.IntegerField(allow_null=True)
    parent_key = serializers.CharField(source="parent.key", allow_null=True)


class KanbanIssueQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    sprint_id = serializers.IntegerField(required=False, min_value=1)
    parent_id = serializers.IntegerField(required=False, min_value=1)
    issue_type = serializers.ChoiceField(choices=ISSUE_TYPE_CHOICES, required=False)
    assignee_id = serializers.IntegerField(required=False, min_value=1)
    priority = serializers.ChoiceField(choices=ISSUE_PRIORITY_CHOICES, required=False)
    sort = serializers.ChoiceField(
        choices=[choice[0] for choice in KANBAN_SORT_CHOICES],
        required=False,
        default="position",
    )


class KanbanIssueStatusSerializer(serializers.Serializer):
    status_id = serializers.IntegerField(min_value=1)


class KanbanIssuePositionSerializer(serializers.Serializer):
    position = serializers.IntegerField(min_value=0)


class KanbanIssueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField()
    title = serializers.CharField()
    issue_type = serializers.CharField()
    status_id = serializers.IntegerField()
    sprint_id = serializers.IntegerField(allow_null=True)
    story_points = serializers.IntegerField(allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    estimated_time = serializers.IntegerField(allow_null=True)
    priority = serializers.CharField()
    assignee_id = serializers.IntegerField(allow_null=True)
    position = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class KanbanSprintFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ["id", "name", "status"]


class IssueCreateSerializer(serializers.Serializer):
    issue_type = serializers.ChoiceField(choices=ISSUE_TYPE_CHOICES)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    sprint_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_time = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    status_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    assignee_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    priority = serializers.ChoiceField(
        choices=ISSUE_PRIORITY_CHOICES, required=False, default="medium"
    )
    story_points = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Issue title cannot be empty.")

        return value


class IssueListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    issue_type = serializers.ChoiceField(choices=ISSUE_TYPE_CHOICES, required=False)
    parent_id = serializers.IntegerField(required=False, min_value=1)
    epic_id = serializers.IntegerField(required=False, min_value=1)
    story_id = serializers.IntegerField(required=False, min_value=1)
    sprint_id = serializers.IntegerField(required=False, min_value=1)
    assignee_id = serializers.IntegerField(required=False, min_value=1)
    priority = serializers.ChoiceField(choices=ISSUE_PRIORITY_CHOICES, required=False)
    status_id = serializers.IntegerField(required=False, min_value=1)
    sort = serializers.ChoiceField(
        choices=[choice[0] for choice in ISSUE_SORT_CHOICES],
        required=False,
        default="position",
    )


class SprintCompleteSerializer(serializers.Serializer):
    incomplete_issue_action = serializers.ChoiceField(
        choices=(
            ("sprint", "Move to Sprint"),
            ("new_sprint", "Create New Sprint"),
            ("backlog", "Move to Backlog"),
        ),
        required=False,
    )
    target_sprint_id = serializers.IntegerField(required=False, min_value=1)

    def validate(self, attrs):
        action = attrs.get("incomplete_issue_action")
        target_sprint_id = attrs.get("target_sprint_id")

        if action == "sprint" and target_sprint_id is None:
            raise serializers.ValidationError(
                {"target_sprint_id": ("Target sprint is required.")}
            )

        if action != "sprint" and target_sprint_id is not None:
            raise serializers.ValidationError(
                {
                    "target_sprint_id": (
                        "Target sprint is only allowed "
                        "when moving issues to another sprint."
                    )
                }
            )

        return attrs


class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = ["id", "name", "color"]


class IssueResponseSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)
    project_id = serializers.IntegerField(source="project.id", read_only=True)
    parent_key = serializers.CharField(
        source="parent.key", read_only=True, allow_null=True
    )
    parent_id = serializers.IntegerField(
        source="parent.id", read_only=True, allow_null=True
    )
    sprint_id = serializers.IntegerField(source="sprint.id", read_only=True)
    sprint_name = serializers.CharField(source="sprint.name", read_only=True)
    status_id = serializers.IntegerField(source="status.id", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)
    assignee_id = serializers.IntegerField(source="assignee.id", read_only=True)
    assignee_name = serializers.CharField(source="assignee.full_name", read_only=True)
    reporter_name = serializers.CharField(source="reporter.full_name", read_only=True)
    labels = LabelSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "key",
            "project_id",
            "parent_key",
            "parent_id",
            "sprint_id",
            "sprint_name",
            "status_id",
            "due_date",
            "estimated_time",
            "status_name",
            "assignee_id",
            "assignee_name",
            "reporter_name",
            "issue_number",
            "issue_type",
            "title",
            "description",
            "priority",
            "story_points",
            "position",
            "labels",
            "created_at",
            "updated_at",
        ]


class IssueUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    sprint_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    status_id = serializers.IntegerField(required=False, min_value=1)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_time = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    assignee_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    priority = serializers.ChoiceField(choices=ISSUE_PRIORITY_CHOICES, required=False)
    story_points = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Issue title cannot be empty.")

        return value


class LabelQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)


class AddLabelSerializer(serializers.Serializer):
    label_id = serializers.IntegerField(required=False, min_value=1)
    name = serializers.CharField(required=False, max_length=50)
    color = serializers.CharField(required=False, max_length=7, default="#999999")

    def validate(self, attrs):
        if not attrs.get("label_id") and not attrs.get("name"):
            raise serializers.ValidationError("Either label_id or name is required.")

        if attrs.get("label_id") and attrs.get("name"):
            raise serializers.ValidationError("Provide either label_id or name.")

        return attrs


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000)
    parent_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Comment cannot be empty.")

        return value


class CommentListQuerySerializer(serializers.Serializer):
    sort = serializers.ChoiceField(
        choices=[choice[0] for choice in COMMENT_SORT_CHOICES],
        required=False,
        default="newest",
    )


class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_profile = serializers.URLField(source="author.avatar", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "issue_id",
            "parent_id",
            "author_profile",
            "author_id",
            "author_name",
            "content",
            "created_at",
            "updated_at",
        ]


class CommentReplySerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_profile = serializers.URLField(source="author.avatar", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "author_id",
            "author_name",
            "author_profile",
            "content",
            "created_at",
            "updated_at",
        ]


class CommentListSerializer(CommentSerializer):
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = [
            "id",
            "issue_id",
            "author_id",
            "author_name",
            "author_profile",
            "content",
            "created_at",
            "updated_at",
            "replies",
        ]


class CommentUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000)

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Comment cannot be empty.")

        return value


class CommentReactionSerializer(serializers.Serializer):
    reaction = serializers.ChoiceField(choices=COMMENT_REACTION_CHOICES)


class CommentReactionSummarySerializer(serializers.Serializer):
    heart = serializers.IntegerField()
    laugh = serializers.IntegerField()
    celebrate = serializers.IntegerField()
    surprised = serializers.IntegerField()
    sad = serializers.IntegerField()
    my_reaction = serializers.CharField(allow_null=True)


class SubtaskListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    sort = serializers.ChoiceField(
        choices=[
            "position",
            "created_asc",
            "created_desc",
            "updated_asc",
            "updated_desc",
        ],
        required=False,
        default="position",
    )


class AttachmentUploadSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    file_size = serializers.IntegerField(min_value=1, max_value=MAX_ATTACHMENT_SIZE)
    mime_type = serializers.CharField(max_length=100)

    def validate_file_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("File name cannot be empty.")

        return value

    def validate_mime_type(self, value):
        value = value.strip().lower()

        if value not in ALLOWED_ATTACHMENT_MIME_TYPES:
            raise serializers.ValidationError("This file type is not supported.")

        return value


class AttachmentUploadCompleteSerializer(serializers.Serializer):
    object_key = serializers.CharField(max_length=500)

    def validate_object_key(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Object key cannot be empty.")

        return value


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_id = serializers.IntegerField(source="uploaded_by.id", read_only=True)
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name", read_only=True
    )
    uploaded_by_avatar = serializers.URLField(
        source="uploaded_by.avatar", read_only=True, allow_null=True
    )
    download_url = serializers.URLField(read_only=True)

    class Meta:
        model = Attachment
        fields = [
            "id",
            "file_name",
            "file_size",
            "mime_type",
            "uploaded_by_id",
            "uploaded_by_name",
            "uploaded_by_avatar",
            "created_at",
            "download_url",
        ]


class DocumentFolderQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)


class DocumentFolderSerializer(serializers.ModelSerializer):
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = DocumentFolder
        fields = [
            "id",
            "name",
            "created_by_id",
            "created_by_name",
            "created_at",
            "updated_at",
        ]


class DocumentFolderCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Folder name cannot be empty.")

        return value


class DocumentQuerySerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(required=False, min_value=1)
    search = serializers.CharField(required=False, allow_blank=True)
    sort = serializers.ChoiceField(
        choices=(
            "updated_desc",
            "updated_asc",
            "created_desc",
            "created_asc",
            "title_asc",
            "title_desc",
        ),
        required=False,
        default="updated_desc",
    )


class DocumentSerializer(serializers.ModelSerializer):
    folder_id = serializers.IntegerField(source="folder.id", read_only=True)
    folder_name = serializers.CharField(source="folder.name", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "folder_id",
            "folder_name",
            "title",
            "created_by_id",
            "created_by_name",
            "current_version",
            "created_at",
            "updated_at",
        ]


class DocumentCreateSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Document title cannot be empty.")

        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Document content cannot be empty.")

        return value


class DocumentDetailSerializer(serializers.ModelSerializer):
    folder_id = serializers.IntegerField(source="folder.id", read_only=True)
    folder_name = serializers.CharField(source="folder.name", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "folder_id",
            "folder_name",
            "title",
            "content",
            "created_by_id",
            "created_by_name",
            "current_version",
            "created_at",
            "updated_at",
        ]


class DocumentUpdateSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(required=False, min_value=1)
    title = serializers.CharField(max_length=255, required=False)
    content = serializers.CharField(required=False)

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Document title cannot be empty.")

        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Document content cannot be empty.")

        return value
