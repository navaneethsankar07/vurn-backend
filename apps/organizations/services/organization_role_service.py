from django.db import transaction
from django.db.models import Q, Count

from ..constants import ORGANIZATION_ROLE_SORT_FIELDS, ORGANIZATION_ROLE_SORT_ORDERS
from ..exceptions import InvalidOrganizationRolePermissionsException
from ..models import (
    OrganizationRole,
    OrganizationRolePermission,
    Permission,
)


class OrganizationRoleService:

    @staticmethod
    def list_roles(
        *,
        organization,
        search=None,
        sort="name",
        order="asc",
    ):
        queryset = (
            OrganizationRole.objects.filter(
                organization=organization,
            )
            .annotate(
                members_count=Count("members"),
            )
            .prefetch_related(
                "role_permissions__permission",
            )
        )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        sort_field = ORGANIZATION_ROLE_SORT_FIELDS.get(
            sort,
            "name",
        )

        sort_prefix = ORGANIZATION_ROLE_SORT_ORDERS.get(
            order,
            "",
        )

        return queryset.order_by(f"{sort_prefix}{sort_field}")

    @staticmethod
    @transaction.atomic
    def create_role(
        *,
        organization,
        name,
        description="",
        color="",
        permission_codes=None,
    ):
        permission_codes = permission_codes or []

        permissions = OrganizationRoleService._get_permissions(
            permission_codes=permission_codes,
        )

        role = OrganizationRole.objects.create(
            organization=organization,
            name=name,
            description=description,
            color=color,
        )

        OrganizationRolePermission.objects.bulk_create(
            [
                OrganizationRolePermission(
                    role=role,
                    permission=permission,
                )
                for permission in permissions
            ]
        )

        return role

    @staticmethod
    @transaction.atomic
    def update_role(
        *,
        organization,
        role_id,
        validated_data,
    ):
        permission_codes = validated_data.pop(
            "permissions",
            None,
        )

        role = OrganizationRole.objects.get(
            id=role_id,
            organization=organization,
        )

        for field, value in validated_data.items():
            setattr(role, field, value)

        role.save()

        if permission_codes is not None:
            permissions = OrganizationRoleService._get_permissions(
                permission_codes=permission_codes,
            )

            OrganizationRolePermission.objects.filter(
                role=role,
            ).delete()

            OrganizationRolePermission.objects.bulk_create(
                [
                    OrganizationRolePermission(
                        role=role,
                        permission=permission,
                    )
                    for permission in permissions
                ]
            )

        return role

    @staticmethod
    def _get_permissions(*, permission_codes):
        if not permission_codes:
            return []

        permissions = list(
            Permission.objects.filter(
                code__in=permission_codes,
            )
        )

        found_codes = {permission.code for permission in permissions}
        invalid_codes = set(permission_codes) - found_codes

        if invalid_codes:
            formatted_codes = ", ".join(sorted(invalid_codes))
            raise InvalidOrganizationRolePermissionsException(
                f"Invalid permission codes: {formatted_codes}"
            )

        return permissions
