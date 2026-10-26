from django.db.models import Q

from apps.accounts.models import User
from apps.shared.services.cloudinary_service import CloudinaryService
from apps.organizations.models import Organization
from apps.projects.models import Comment, Issue, Project
from apps.integrations.models import GitIntegration
from ..constants import CLOUDINARY_AVATAR_FOLDER


class ProfileService:

    @staticmethod
    def get_profile(user: User) -> dict:

        organizations_count = (
            Organization.objects.filter(
                Q(owner=user) | Q(members__user=user),
                is_archived=False,
                deleted_at__isnull=True,
            )
            .distinct()
            .count()
        )

        projects_count = (
            Project.objects.filter(
                Q(owner=user) | Q(created_by=user) | Q(members__user=user),
                is_archived=False,
                deleted_at__isnull=True,
            )
            .distinct()
            .count()
        )

        assigned_issues_count = Issue.objects.filter(
            assignee=user,
            deleted_at__isnull=True,
        ).count()

        completed_issues_count = (
            Issue.objects.filter(
                Q(assignee=user) | Q(reporter=user),
                status__category="done",
                deleted_at__isnull=True,
            )
            .distinct()
            .count()
        )

        comments_count = Comment.objects.filter(
            author=user,
            deleted_at__isnull=True,
        ).count()

        github_linked_projects_count = (
            GitIntegration.objects.filter(
                Q(project__organization__owner=user)
                | (
                    Q(project__organization__members__user=user)
                    & Q(project__members__user=user)
                ),
                provider="github",
                status="active",
                project__is_archived=False,
                project__deleted_at__isnull=True,
            )
            .values("project_id")
            .distinct()
            .count()
        )

        return {
            "user": user,
            "statistics": {
                "organizations": organizations_count,
                "projects": projects_count,
                "assigned_issues": assigned_issues_count,
                "completed_issues": completed_issues_count,
                "comments": comments_count,
                "github_linked_projects": github_linked_projects_count,
            },
        }

    @staticmethod
    def update_profile(
        user: User,
        validated_data: dict,
    ) -> User:

        avatar = validated_data.pop("avatar", None)

        for field, value in validated_data.items():
            setattr(user, field, value)

        update_fields = list(validated_data.keys())

        if avatar is not None:
            avatar_url = CloudinaryService.upload(
                avatar,
                folder=CLOUDINARY_AVATAR_FOLDER,
            )

            user.avatar = avatar_url
            update_fields.append("avatar")

        if update_fields:
            update_fields.append("updated_at")

            user.save(
                update_fields=update_fields,
            )

        return user
