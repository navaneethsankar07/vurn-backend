from apps.organizations.models import Organization
from apps.shared.services.cloudinary_service import (
    CloudinaryService,
)


class OrganizationBrandingService:

    FOLDER = "vurn/organizations"

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
                folder=OrganizationBrandingService.FOLDER,
            )

            data["logo_url"] = logo_url

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
