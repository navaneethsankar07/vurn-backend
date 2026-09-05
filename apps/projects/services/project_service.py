from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify

from apps.shared.services.cloudinary_service import CloudinaryService

from ..constants import (
    CLOUDINARY_PROJECTS_FOLDER,
    PROJECT_ARCHIVE_FILTERS,
    PROJECT_LIST_SORT_OPTIONS,
)
from ..exceptions import (
    ProjectAlreadyExistsException,
    ProjectNotFoundException,
)
from ..models import Project


class ProjectService:

    @staticmethod
    def _generate_slug(
        *,
        organization,
        name,
        exclude_project_id=None,
    ) -> str:
        base_slug = slugify(name) or "project"
        slug = base_slug
        counter = 2

        queryset = Project.objects.filter(
            organization=organization,
        )

        if exclude_project_id:
            queryset = queryset.exclude(
                id=exclude_project_id,
            )

        while queryset.filter(
            slug=slug,
        ).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @staticmethod
    def get_project(
        *,
        organization,
        slug,
    ) -> Project:
        try:
            return Project.objects.select_related(
                "organization",
                "owner",
                "project_lead",
                "created_by",
            ).get(
                organization=organization,
                slug=slug,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist as exc:
            raise ProjectNotFoundException("Project not found.") from exc

    @staticmethod
    def list_projects(
        *,
        organization,
        search=None,
        status="all",
        archive="active",
        sort="recently_created",
    ):
        queryset = Project.objects.filter(
            organization=organization,
            deleted_at__isnull=True,
        ).select_related(
            "owner",
            "project_lead",
            "created_by",
        )

        if archive not in PROJECT_ARCHIVE_FILTERS:
            archive = "active"

        if archive == "active":
            queryset = queryset.filter(
                is_archived=False,
            )
        elif archive == "archived":
            queryset = queryset.filter(
                is_archived=True,
            )

        if status and status != "all":
            queryset = queryset.filter(
                status=status,
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(key__icontains=search)
            )

        if sort not in PROJECT_LIST_SORT_OPTIONS:
            sort = "recently_created"

        sort_options = {
            "recently_created": "-created_at",
            "recently_updated": "-updated_at",
            "name_asc": "name",
            "name_desc": "-name",
        }

        return queryset.order_by(
            sort_options[sort],
        )

    @staticmethod
    @transaction.atomic
    def create_project(
        *,
        organization,
        user,
        name,
        key,
        description="",
        icon="hexagon",
        accent_color="#F59E0B",
        start_date=None,
        target_date=None,
    ) -> Project:
        if Project.objects.filter(
            organization=organization,
            key=key,
        ).exists():
            raise ProjectAlreadyExistsException(
                "A project with this key already exists " "in this organization."
            )

        slug = ProjectService._generate_slug(
            organization=organization,
            name=name,
        )

        try:
            project = Project.objects.create(
                organization=organization,
                owner=user,
                project_lead=user,
                created_by=user,
                name=name,
                key=key,
                slug=slug,
                description=description,
                icon=icon,
                accent_color=accent_color,
                start_date=start_date,
                target_date=target_date,
            )
        except IntegrityError as exc:
            raise ProjectAlreadyExistsException(
                "Unable to create the project."
            ) from exc

        return project

    @staticmethod
    @transaction.atomic
    def update_project(
        *,
        project,
        **validated_data,
    ) -> Project:
        logo = validated_data.pop(
            "logo",
            None,
        )

        icon_provided = "icon" in validated_data

        name = validated_data.get(
            "name",
        )

        key = validated_data.get(
            "key",
        )

        if key and key != project.key:
            if (
                Project.objects.filter(
                    organization=project.organization,
                    key=key,
                )
                .exclude(
                    id=project.id,
                )
                .exists()
            ):
                raise ProjectAlreadyExistsException(
                    "A project with this key already exists " "in this organization."
                )

        if name and name != project.name:
            project.slug = ProjectService._generate_slug(
                organization=project.organization,
                name=name,
                exclude_project_id=project.id,
            )

        for field, value in validated_data.items():
            setattr(
                project,
                field,
                value,
            )

        if logo is not None:
            project.logo_url = CloudinaryService.upload(
                logo,
                folder=(
                    f"{CLOUDINARY_PROJECTS_FOLDER}/"
                    f"{project.organization_id}/logos"
                ),
            )
        elif icon_provided:
            project.logo_url = None

        try:
            project.save()
        except IntegrityError as exc:
            raise ProjectAlreadyExistsException(
                "Unable to update the project because "
                "the project key already exists."
            ) from exc

        return project
