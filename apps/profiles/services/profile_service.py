from django.db.models import Q

from apps.accounts.models import User
from apps.shared.services.cloudinary_service import CloudinaryService
from apps.organizations.models import Organization
from apps.projects.models import Project
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

        return {
            "user": user,
            "statistics": {
                "organizations": organizations_count,
                "projects": projects_count,
                "assigned_issues": 42,
                "completed_issues": 128,
                "comments": 356,
                "github_linked_projects": 9,
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
