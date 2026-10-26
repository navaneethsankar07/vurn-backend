from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class EmailService:

    @staticmethod
    def send_email(
        *,
        subject: str,
        message: str,
        recipient_list: list,
        html_message: str | None = None,
    ) -> None:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_otp_email(
        *,
        recipient_email: str,
        otp: str,
    ) -> None:

        otp_expiration_minutes = settings.OTP_EXPIRATION_SECONDS // 60

        html_message = render_to_string(
            "emails/otp_verification.html",
            {
                "otp": otp,
                "otp_expiration_minutes": otp_expiration_minutes,
            },
        )

        EmailService.send_email(
            subject="Verify your Vurn account",
            message=(
                f"Your verification code is {otp}.\n\n"
                f"This code will expire in "
                f"{otp_expiration_minutes} minutes."
            ),
            recipient_list=[recipient_email],
            html_message=html_message,
        )

    @staticmethod
    def send_password_reset_email(
        *,
        recipient_email: str,
        reset_link: str,
    ) -> None:

        password_reset_expiration_minutes = (
            settings.PASSWORD_RESET_EXPIRATION_SECONDS // 60
        )

        html_message = render_to_string(
            "emails/password_reset.html",
            {
                "reset_link": reset_link,
                "password_reset_expiration_minutes": (
                    password_reset_expiration_minutes
                ),
            },
        )

        EmailService.send_email(
            subject="Reset your Vurn password",
            message=(
                "We received a request to reset your password.\n\n"
                f"Reset your password:\n{reset_link}\n\n"
                "This link expires in "
                f"{password_reset_expiration_minutes} minutes.\n\n"
                "If you didn't request this, you can safely ignore "
                "this email."
            ),
            recipient_list=[recipient_email],
            html_message=html_message,
        )

    @staticmethod
    def send_account_deletion_otp_email(
        *,
        recipient_email: str,
        otp: str,
    ) -> None:

        otp_expiration_minutes = settings.OTP_EXPIRATION_SECONDS // 60

        html_message = render_to_string(
            "emails/account_deletion.html",
            {
                "otp": otp,
                "otp_expiration_minutes": otp_expiration_minutes,
            },
        )

        EmailService.send_email(
            subject="Confirm your Vurn account deletion",
            message=(
                "We received a request to delete your Vurn account.\n\n"
                f"Your verification code is {otp}.\n\n"
                "This code will expire in "
                f"{otp_expiration_minutes} minutes.\n\n"
                "If you did not request this, you can safely ignore "
                "this email."
            ),
            recipient_list=[recipient_email],
            html_message=html_message,
        )

    @staticmethod
    def send_organization_deletion_otp_email(
        *,
        recipient_email: str,
        otp: str,
        organization_name: str,
    ) -> None:

        otp_expiration_minutes = settings.OTP_EXPIRATION_SECONDS // 60

        html_message = render_to_string(
            "emails/organization_deletion.html",
            {
                "otp": otp,
                "organization_name": organization_name,
                "otp_expiration_minutes": otp_expiration_minutes,
            },
        )

        EmailService.send_email(
            subject="Confirm organization deletion",
            message=(
                f"We received a request to delete "
                f"the organization {organization_name}.\n\n"
                f"Your verification code is {otp}.\n\n"
                f"This code will expire in "
                f"{otp_expiration_minutes} minutes."
            ),
            recipient_list=[recipient_email],
            html_message=html_message,
        )

    @staticmethod
    def send_organization_invitation_email(
        *,
        recipient_email: str,
        organization_name: str,
        invitation_link: str,
        personal_message: str = "",
        expires_at,
    ) -> None:
        html_message = render_to_string(
            "emails/organization_invitation.html",
            {
                "organization_name": organization_name,
                "invitation_link": invitation_link,
                "personal_message": personal_message,
                "expires_at": expires_at,
            },
        )

        message = f"You have been invited to join " f"{organization_name} on Vurn.\n\n"

        if personal_message:
            message += f"Personal message:\n" f"{personal_message}\n\n"

        message += (
            f"Join the organization:\n"
            f"{invitation_link}\n\n"
            f"This invitation expires at {expires_at}."
        )

        EmailService.send_email(
            subject=f"You're invited to join {organization_name} on Vurn",
            message=message,
            recipient_list=[recipient_email],
            html_message=html_message,
        )
