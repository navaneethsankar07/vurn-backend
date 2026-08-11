from django.db import transaction

from ..constants import OTP_ACCOUNT_DELETION_PREFIX
from ..exceptions import (
    InvalidAccountDeletionOTPException,
)
from ..models import User
from .email_service import EmailService
from .otp_service import OTPService


class AccountDeletionService:

    @staticmethod
    def send_deletion_otp(user: User) -> None:
        OTPService.delete(
            OTP_ACCOUNT_DELETION_PREFIX,
            user.email,
        )

        otp = OTPService.generate(
            OTP_ACCOUNT_DELETION_PREFIX,
            user.email,
        )

        EmailService.send_account_deletion_otp_email(
            recipient_email=user.email,
            otp=otp,
        )

    @staticmethod
    @transaction.atomic
    def delete_account(
        user: User,
        otp: str,
    ) -> None:

        if not OTPService.verify(
            OTP_ACCOUNT_DELETION_PREFIX,
            user.email,
            otp,
        ):
            raise InvalidAccountDeletionOTPException("Invalid or expired OTP.")

        user.is_active = False

        user.save(
            update_fields=[
                "is_active",
                "updated_at",
            ],
        )
