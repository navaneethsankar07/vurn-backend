from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.services.organization_service import OrganizationService
from apps.projects.services.project_service import ProjectService
from apps.recent_activities.models import RecentActivity
from apps.recent_activities.serializers import RecentActivitySerializer
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.projects.exceptions import ProjectNotFoundException
from apps.projects.models import Sprint
from .services.recent_activity_service import RecentActivityService


class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = request.query_params.get("scope", "home")

        try:
            if scope == "home":
                activities = RecentActivity.objects.filter(
                    Q(organization__owner=request.user)
                    | Q(organization__members=request.user)
                )

            elif scope == "organization":
                organization = OrganizationService.get_user_organization(
                    user=request.user,
                    slug=request.query_params.get("organization_slug", ""),
                )
                activities = RecentActivityService.get_organization_activities(
                    organization=organization
                )

            elif scope == "project":
                organization = OrganizationService.get_user_organization(
                    user=request.user,
                    slug=request.query_params.get("organization_slug", ""),
                )
                project = ProjectService.get_project(
                    organization=organization,
                    slug=request.query_params.get("project_slug", ""),
                )
                activities = RecentActivityService.get_project_activities(
                    project=project
                )

            elif scope == "sprint":
                organization = OrganizationService.get_user_organization(
                    user=request.user,
                    slug=request.query_params.get("organization_slug", ""),
                )
                project = ProjectService.get_project(
                    organization=organization,
                    slug=request.query_params.get("project_slug", ""),
                )
                sprint = Sprint.objects.filter(
                    id=request.query_params.get("sprint_id"), project=project
                ).first()

                if sprint is None:
                    return Response(
                        {"error": "Sprint not found."}, status=status.HTTP_404_NOT_FOUND
                    )

                activities = RecentActivityService.get_sprint_activities(sprint=sprint)

            else:
                return Response(
                    {
                        "error": "Invalid scope. Use home, organization, project, or sprint."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        activities = (
            activities.select_related("actor", "project", "sprint", "issue")
            .order_by("-created_at")
            .distinct()[:5]
        )

        serializer = RecentActivitySerializer(activities, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
