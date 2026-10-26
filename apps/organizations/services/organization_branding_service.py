from apps.organizations.models import Organization
from apps.shared.services.cloudinary_service import (
    CloudinaryService,
)
from ..constants import CLOUDINARY_ORGANIZATIONS_FOLDER


class OrganizationBrandingService:

    @staticmethod
    def update_branding(
        *,
        organization: Organization,
        validated_data: dict,
    ) -> Organization:

        data = validated_data.copy()

        logo = data.pop(
            "logo",
            None,
        )

        if logo is not None:
            logo_url = CloudinaryService.upload(
                logo,
                folder=CLOUDINARY_ORGANIZATIONS_FOLDER,
            )
            data["logo_url"] = logo_url
        elif "icon" in data:
            data["logo_url"] = None

        for field, value in data.items():
            setattr(
                organization,
                field,
                value,
            )

        organization.save(
            update_fields=[
                *data.keys(),
                "updated_at",
            ],
        )

        return organization
