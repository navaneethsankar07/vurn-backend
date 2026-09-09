from django.db import IntegrityError, transaction

from backend.apps.accounts.models import User
from backend.apps.organizations.models import OrganizationMember
from backend.apps.projects.exceptions import (
    ProjectMemberAlreadyExistsException,
    ProjectMemberUserNotFoundException,
)
from backend.apps.projects.models import ProjectMember


class ProjectMemberService:

    @staticmethod
    def get_project_member(*, project, user_id):
        try:
            return ProjectMember.objects.select_related("user").get(
                project=project, user_id=user_id
            )
        except ProjectMember.DoesNotExist as exc:
            raise ProjectMemberUserNotFoundException(
                "Project member not found."
            ) from exc

    @staticmethod
    @transaction.atomic
    def add_member(*, project, user_id, project_role=None) -> ProjectMember:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as exc:
            raise ProjectMemberUserNotFoundException("User not found.") from exc

        is_organization_owner = project.organization.owner_id == user.id

        is_organization_member = OrganizationMember.objects.filter(
            organization=project.organization, user=user
        ).exists()

        if not is_organization_owner and not is_organization_member:
            raise ProjectMemberUserNotFoundException(
                "User is not a member of this organization."
            )

        if ProjectMember.objects.filter(project=project, user=user).exists():
            raise ProjectMemberAlreadyExistsException(
                "User is already a member of this project."
            )

        if not project_role:
            if is_organization_owner:
                project_role = "Owner"
            else:
                membership = OrganizationMember.objects.select_related("job_role").get(
                    organization=project.organization, user=user
                )

                if membership.job_role:
                    project_role = membership.job_role.name
                else:
                    project_role = "Member"

        try:
            return ProjectMember.objects.create(
                project=project, user=user, project_role=project_role
            )
        except IntegrityError as exc:
            raise ProjectMemberAlreadyExistsException(
                "User is already a member of this project."
            ) from exc
