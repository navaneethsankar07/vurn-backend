from django.utils import timezone

from apps.shared.services.email_service import EmailService
from apps.accounts.services.otp_service import OTPService
from apps.organizations.constants import (
    ORGANIZATION_DELETE_OTP_PREFIX,
)
from apps.organizations.exceptions import (
    InvalidOrganizationDeleteOTPException,
    OrganizationAlreadyDeletedException,
    OrganizationNameMismatchException,
)
from apps.organizations.models import Organization


class OrganizationDeletionService:

    @staticmethod
    def _identifier(
        *,
        user,
        organization,
    ) -> str:
        return f"{user.id}:" f"{organization.id}"

    @classmethod
    def request_deletion(
        cls,
        *,
        user,
        organization: Organization,
        name: str,
    ) -> None:

        if organization.deleted_at is not None:
            raise OrganizationAlreadyDeletedException(
                "Organization has already been deleted."
            )

        if organization.name != name:
            raise OrganizationNameMismatchException("Organization name does not match.")

        identifier = cls._identifier(
            user=user,
            organization=organization,
        )

        OTPService.delete(
            ORGANIZATION_DELETE_OTP_PREFIX,
            identifier,
        )

        otp = OTPService.generate(
            ORGANIZATION_DELETE_OTP_PREFIX,
            identifier,
        )

        EmailService.send_organization_deletion_otp_email(
            recipient_email=user.email,
            otp=otp,
            organization_name=organization.name,
        )

    @classmethod
    def confirm_deletion(
        cls,
        *,
        user,
        organization: Organization,
        otp: str,
    ) -> None:

        if organization.deleted_at is not None:
            raise OrganizationAlreadyDeletedException(
                "Organization has already been deleted."
            )

        identifier = cls._identifier(
            user=user,
            organization=organization,
        )

        if not OTPService.verify(
            ORGANIZATION_DELETE_OTP_PREFIX,
            identifier,
            otp,
        ):
            raise InvalidOrganizationDeleteOTPException("Invalid or expired OTP.")

        organization.is_archived = True
        organization.deleted_at = timezone.now()

        organization.save(
            update_fields=[
                "is_archived",
                "deleted_at",
                "updated_at",
            ],
        )
