from django.conf import settings
from django.core.mail import send_mail


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
    def send_otp_email(*, recipient_email: str, otp: str) -> None:
        EmailService.send_email(
            subject="Verify your Vurtual Account",
            message=(
                f"Your verification code is {otp}.\n\n"
                "This code will expire in 5 minutes."
            ),
            recipient_list=[recipient_email],
        )

    @staticmethod
    def send_password_reset_email(
        recipient_email: str,
        reset_link: str,
    ) -> None:

        subject = "Reset Your Vurn Password"

        message = (
            "We received a request to reset your password.\n\n"
            f"Reset your password:\n{reset_link}\n\n"
            "This link expires in 10 minutes.\n\n"
            "If you didn't request this, you can safely ignore this email."
        )

        EmailService.send_email(
            subject=subject,
            message=message,
            recipient_list=[recipient_email],
        )