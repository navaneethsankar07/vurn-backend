from django.db import transaction

from ..exceptions import CommentInvalidException, CommentNotFoundException, CommentPermissionException
from ..models import Comment


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
