from apps.accounts.models import User


class LoginMethodService:

    @staticmethod
    def is_email_login(user: User) -> bool:
        return user.has_usable_password()
