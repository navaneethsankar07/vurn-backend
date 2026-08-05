from apps.accounts.models import User


class ProfileService:

    @staticmethod
    def get_current_user(user: User) -> User:
        return user
