from apps.organizations.constants import (
    ORGANIZATION_ACCENT_COLORS,
    ORGANIZATION_ICONS,
)


class OrganizationOptionsService:

    @staticmethod
    def get_options() -> dict:
        return {
            "icons": list(ORGANIZATION_ICONS),
            "accent_colors": [
                {
                    "name": name,
                    "value": value,
                }
                for name, value in ORGANIZATION_ACCENT_COLORS.items()
            ],
        }
