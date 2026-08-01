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
