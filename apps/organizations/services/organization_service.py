from django.db import transaction

from apps.accounts.models import User
from apps.organizations.models import Organization


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
