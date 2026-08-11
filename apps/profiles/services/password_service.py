from django.db import transaction

from ..exceptions import (
    InvalidCurrentPasswordException,
)
from apps.accounts.models import User


class PasswordService:

    @staticmethod
    @transaction.atomic
    def change_password(
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:

        if not user.check_password(current_password):
            raise InvalidCurrentPasswordException("Current password is incorrect.")

        user.set_password(new_password)

        user.save(
            update_fields=[
                "password",
                "updated_at",
            ],
        )
