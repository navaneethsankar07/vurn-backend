from django.db import IntegrityError, transaction

from apps.accounts.models import User
from apps.organizations.models import OrganizationMember
from apps.projects.models import ProjectMember

from ..exceptions import (
    ProjectMemberAlreadyExistsException,
    ProjectMemberNotFoundException,
    ProjectMemberUserNotFoundException,
)


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

    @staticmethod
    def list_members(*, project, search=None, sort="recently_added"):
        members = (
            ProjectMember.objects.filter(project=project)
            .select_related("user")
            .order_by("joined_at")
        )

        owner = project.owner

        result = [
            {
                "id": None,
                "user_id": owner.id,
                "full_name": owner.full_name or "",
                "email": owner.email,
                "avatar": owner.avatar,
                "project_role": "Project Owner",
                "joined_at": project.created_at,
            }
        ]

        result.extend(
            {
                "id": member.id,
                "user_id": member.user.id,
                "full_name": member.user.full_name or "",
                "email": member.user.email,
                "avatar": member.user.avatar,
                "project_role": member.project_role,
                "joined_at": member.joined_at,
            }
            for member in members
        )

        if search:
            search = search.strip().lower()

            result = [
                member
                for member in result
                if search in member["full_name"].lower()
                or search in member["email"].lower()
                or search in member["project_role"].lower()
            ]

        if sort == "name_asc":
            result.sort(key=lambda member: member["full_name"].lower())
        elif sort == "name_desc":
            result.sort(key=lambda member: member["full_name"].lower(), reverse=True)
        elif sort == "recently_joined":
            result.sort(key=lambda member: member["joined_at"], reverse=True)

        return result

    @staticmethod
    @transaction.atomic
    def remove_member(*, project, user_id) -> None:
        if project.owner_id == user_id:
            raise ProjectMemberNotFoundException("The project owner cannot be removed.")

        try:
            member = ProjectMember.objects.get(project=project, user_id=user_id)
        except ProjectMember.DoesNotExist as exc:
            raise ProjectMemberNotFoundException("Project member not found.") from exc

        member.delete()
