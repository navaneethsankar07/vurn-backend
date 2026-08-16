from backend.apps.shared.services.email_service import EmailService
from apps.accounts.services.otp_service import OTPService
from apps.organizations.constants import (
    ORGANIZATION_DELETE_OTP_PREFIX,
)
from apps.organizations.exceptions import (
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

        EmailService.send_account_deletion_otp_email(
            recipient_email=user.email,
            otp=otp,
        )
