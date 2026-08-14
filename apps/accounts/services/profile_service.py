from django.db.models import Prefetch

from apps.accounts.models import User
from apps.organizations.models import Organization


class ProfileService:

    @staticmethod
    def get_current_user(user: User) -> User:
        return User.objects.prefetch_related("owned_organizations").get(pk=user.pk)
