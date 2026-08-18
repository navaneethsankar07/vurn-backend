from django.db import transaction

from ..constants import ORGANIZATION_PREFERENCE_DEFAULTS
from ..models import OrganizationPreference


class OrganizationPreferenceService:

    @staticmethod
    def get_preferences(*, organization):
        return OrganizationPreference.objects.get(
            organization=organization,
        )

    @staticmethod
    @transaction.atomic
    def update_preferences(*, organization, validated_data):
        preferences = OrganizationPreference.objects.get(
            organization=organization,
        )

        for field, value in validated_data.items():
            setattr(preferences, field, value)

        preferences.save()

        return preferences
