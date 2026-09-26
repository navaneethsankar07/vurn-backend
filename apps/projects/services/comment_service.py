from django.db import transaction
from django.utils import timezone

from ..exceptions import (
    CommentInvalidException,
    CommentNotFoundException,
    CommentPermissionException,
)
from ..models import Comment, CommentReaction


class CommentService:

    @staticmethod
    @transaction.atomic
    def create_comment(*, issue, user, content, parent_id=None):
        parent = None

        if parent_id is not None:
            parent = Comment.objects.filter(
                id=parent_id, issue=issue, deleted_at__isnull=True
            ).first()

            if parent is None:
                raise CommentInvalidException(
                    "The parent comment does not belong " "to this issue."
                )

            if parent.parent_id is not None:
                raise CommentInvalidException("Replies cannot have replies.")

        return Comment.objects.create(
            issue=issue, author=user, parent=parent, content=content
        )

    @staticmethod
    def list_comments(*, issue):
        return (
            Comment.objects.filter(
                issue=issue, parent__isnull=True, deleted_at__isnull=True
            )
            .select_related("author")
            .prefetch_related("replies__author")
            .order_by("created_at")
        )

    @staticmethod
    def update_comment(*, issue, comment_id, user, content):
        comment = Comment.objects.filter(
            id=comment_id, issue=issue, deleted_at__isnull=True
        ).first()

        if comment is None:
            raise CommentNotFoundException("Comment not found.")

        if comment.author_id != user.id:
            raise CommentPermissionException("You can only edit your own comments.")

        comment.content = content
        comment.save(update_fields=["content", "updated_at"])

        return comment

    @staticmethod
    def delete_comment(*, issue, comment_id, user):
        comment = Comment.objects.filter(
            id=comment_id, issue=issue, deleted_at__isnull=True
        ).first()

        if comment is None:
            raise CommentNotFoundException("Comment not found.")

        if comment.author_id != user.id:
            raise CommentPermissionException("You can only delete your own comments.")

        comment.deleted_at = timezone.now()
        comment.save(update_fields=["deleted_at"])

    @staticmethod
    @transaction.atomic
    def set_reaction(*, issue, comment_id, user, reaction):
        comment = Comment.objects.filter(
            id=comment_id, issue=issue, deleted_at__isnull=True
        ).first()

        if comment is None:
            raise CommentNotFoundException("Comment not found.")

        comment_reaction, created = CommentReaction.objects.get_or_create(
            comment=comment, user=user, defaults={"reaction": reaction}
        )

        if not created and comment_reaction.reaction != reaction:
            comment_reaction.reaction = reaction
            comment_reaction.save(update_fields=["reaction", "updated_at"])

        return comment_reaction
