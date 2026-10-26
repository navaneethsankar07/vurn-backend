from django.db import transaction

from apps.organizations.exceptions import (
    OrganizationPinLimitExceededException,
)
from apps.organizations.models import Organization
from ..constants import MAX_PINNED_ORGANIZATIONS
from .organization_service import OrganizationService


class OrganizationPinService:
    

    @staticmethod
    @transaction.atomic
    def update_pin(*, user, slug: str, is_pinned: bool):
        organization = OrganizationService.get_user_organization(user=user, slug=slug)

        if organization.is_pinned == is_pinned:
            return organization

        if is_pinned:
            pinned_count = (
                Organization.objects.select_for_update()
                .filter(is_pinned=True, is_archived=False, deleted_at__isnull=True)
                .count()
            )

            if pinned_count >= MAX_PINNED_ORGANIZATIONS:
                raise OrganizationPinLimitExceededException(
                    "You can pin a maximum of 3 organizations."
                )

        organization.is_pinned = is_pinned
        organization.save(update_fields=["is_pinned"])

        return organization
