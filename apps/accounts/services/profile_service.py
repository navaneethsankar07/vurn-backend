from django.db.models import Prefetch

from apps.accounts.models import User
from apps.organizations.models import Organization


class ProfileService:

    @staticmethod
    def get_current_user(user: User) -> User:
        active_organizations = Organization.objects.filter(
            is_archived=False,
            deleted_at__isnull=True,
        )

        return User.objects.prefetch_related(
            Prefetch("owned_organizations", queryset=active_organizations)
        ).get(pk=user.pk)
