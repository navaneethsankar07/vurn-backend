from django.db import IntegrityError
from django.db import transaction
from django.utils.text import slugify

from ..exceptions import ProjectAlreadyExistsException
from ..models import Project


class ProjectService:

    @staticmethod
    def _generate_slug(
        *,
        organization,
        name,
    ) -> str:
        base_slug = slugify(name) or "project"

        slug = base_slug

        counter = 2

        while Project.objects.filter(
            organization=organization,
            slug=slug,
        ).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

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
                "A project with this key already exists in this organization."
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
                "Unable to create the project because a project with the same identifier already exists."
            ) from exc

        return project
