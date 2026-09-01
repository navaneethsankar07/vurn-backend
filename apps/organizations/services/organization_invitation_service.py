from django.db import transaction
from django.utils import timezone
from apps.accounts.models import User

from ..constants import ORGANIZATION_INVITATION_EXPIRY_DELTA
from ..exceptions import (
    OrganizationInvitationAlreadyExistsException,
    OrganizationInvitationEmailMismatchException,
    OrganizationInvitationExpiredException,
    OrganizationInvitationNotFoundException,
    OrganizationInvitationRecipientAlreadyMemberException,
    OrganizationInvitationRecipientIsOwnerException,
    OrganizationMemberAlreadyExistsException,
)
from ..models import (
    OrganizationInvitation,
    OrganizationMember,
    OrganizationRole,
)


class OrganizationInvitationService:

    @staticmethod
    @transaction.atomic
    def create_invitation(
        *,
        organization,
        invited_by,
        email,
        personal_message="",
        permission_role="member",
        job_role_id=None,
    ):
        email = email.lower()

        if organization.owner.email.lower() == email:
            raise OrganizationInvitationRecipientIsOwnerException(
                "The organization owner cannot be invited."
            )

        user = User.objects.filter(
            email__iexact=email,
        ).first()

        if (
            user
            and OrganizationMember.objects.filter(
                organization=organization,
                user=user,
            ).exists()
        ):
            raise OrganizationInvitationRecipientAlreadyMemberException(
                "This user is already a member of the organization."
            )

        existing_invitation = OrganizationInvitation.objects.filter(
            organization=organization,
            email__iexact=email,
            expires_at__gt=timezone.now(),
        ).first()

        if existing_invitation:
            raise OrganizationInvitationAlreadyExistsException(
                "An active invitation already exists for this email."
            )

        OrganizationInvitation.objects.filter(
            organization=organization,
            email__iexact=email,
            expires_at__lte=timezone.now(),
        ).delete()

        job_role = OrganizationRole.objects.get(
            id=job_role_id,
            organization=organization,
        )

        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            email=email,
            personal_message=personal_message,
            permission_role=permission_role,
            job_role=job_role,
            invited_by=invited_by,
            expires_at=(timezone.now() + ORGANIZATION_INVITATION_EXPIRY_DELTA),
        )

        return invitation

    @staticmethod
    def list_received_invitations(*, user):
        expired_invitations = OrganizationInvitation.objects.filter(
            email__iexact=user.email,
            expires_at__lte=timezone.now(),
        )

        expired_invitations.delete()

        return (
            OrganizationInvitation.objects.filter(
                email__iexact=user.email,
                expires_at__gt=timezone.now(),
            )
            .select_related(
                "organization",
                "job_role",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_invitation_by_token(*, token):
        try:
            invitation = OrganizationInvitation.objects.select_related(
                "organization",
                "job_role",
            ).get(token=token)
        except OrganizationInvitation.DoesNotExist:
            raise OrganizationInvitationNotFoundException("Invitation not found.")

        if invitation.expires_at <= timezone.now():
            invitation.delete()

            raise OrganizationInvitationExpiredException("This invitation has expired.")

        return invitation

    @staticmethod
    @transaction.atomic
    def accept_invitation(
        *,
        token,
        user,
    ):
        invitation = OrganizationInvitationService.get_invitation_by_token(
            token=token,
        )

        if user.email.lower() != invitation.email.lower():
            raise OrganizationInvitationEmailMismatchException(
                "This invitation was sent to another email address."
            )

        if OrganizationMember.objects.filter(
            organization=invitation.organization,
            user=user,
        ).exists():
            invitation.delete()

            raise OrganizationMemberAlreadyExistsException(
                "You are already a member of this organization."
            )

        member = OrganizationMember.objects.create(
            organization=invitation.organization,
            user=user,
            role=invitation.permission_role,
            job_role=invitation.job_role,
            invited_by=invitation.invited_by,
        )

        invitation.delete()

        return member
