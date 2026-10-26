from rest_framework import serializers

from ..constants import COMMENT_REACTION_CHOICES, COMMENT_SORT_CHOICES

from ..models import Comment


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
