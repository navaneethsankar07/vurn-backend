from django.db import transaction

from apps.accounts.models import User
from ..models import Organization, OrganizationPreference
from ..exceptions import (
    OrganizationAlreadyArchivedException,
    OrganizationNotFoundException,
)
from ..constants import ORGANIZATION_PREFERENCE_DEFAULTS


class OrganizationService:

    @staticmethod
    @transaction.atomic
    def create_organization(
        *,
        owner: User,
        name: str,
        description: str,
        slug: str,
        icon: str,
        accent_color: str,
    ) -> Organization:

        organization = Organization.objects.create(
            name=name,
            description=description,
            slug=slug,
            owner=owner,
            icon=icon,
            accent_color=accent_color,
        )

        OrganizationPreference.objects.create(
            organization=organization,
            **ORGANIZATION_PREFERENCE_DEFAULTS,
        )

        return organization

    @staticmethod
    def update_settings(
        *,
        organization: Organization,
        validated_data: dict,
    ) -> Organization:

        for field, value in validated_data.items():
            setattr(
                organization,
                field,
                value,
            )

        organization.save(
            update_fields=[
                *validated_data.keys(),
                "updated_at",
            ],
        )

        return organization

    @staticmethod
    def get_owned_organization(
        *,
        user,
        slug: str,
    ) -> Organization:

        organization = Organization.objects.filter(
            owner=user,
            slug=slug,
            deleted_at__isnull=True,
        ).first()

        if organization is None:
            raise OrganizationNotFoundException("Organization not found.")

        return organization

    @staticmethod
    def archive(
        *,
        organization: Organization,
    ) -> Organization:

        if organization.is_archived:
            raise OrganizationAlreadyArchivedException(
                "Organization is already archived."
            )

        organization.is_archived = True

        organization.save(
            update_fields=[
                "is_archived",
                "updated_at",
            ],
        )

        return organization
