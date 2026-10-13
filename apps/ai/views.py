from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import (
    AIConfigurationError,
    AIProviderError,
    AIResponseError,
    AIStructuredOutputError,
)
from .serializers import (
    StoryPointEstimationResponseSerializer,
    TaskBreakdownRequestSerializer,
    TaskBreakdownResponseSerializer,
)
from .services.task_breakdown_service import TaskBreakdownService
from .services.story_point_estimation_service import StoryPointEstimationService
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService
from apps.projects.exceptions import IssueNotFoundException, ProjectNotFoundException
from apps.projects.services.issue_service import IssueService
from apps.projects.services.project_service import ProjectService


class TaskBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = TaskBreakdownRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            result = TaskBreakdownService.generate_breakdown(
                **request_serializer.validated_data
            )
        except AIConfigurationError:
            return Response(
                {"detail": "AI service is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIProviderError:
            return Response(
                {"detail": "AI provider is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIStructuredOutputError:
            return Response(
                {"detail": "AI could not generate a valid task breakdown."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIResponseError:
            return Response(
                {"detail": "AI returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response_serializer = TaskBreakdownResponseSerializer(data=result)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.validated_data, status=status.HTTP_200_OK)


class StoryPointEstimationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, project_slug, issue_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
            issue = IssueService.get_issue(project=project, issue_id=issue_id)
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        try:
            result = StoryPointEstimationService.estimate(issue=issue)
        except AIConfigurationError:
            return Response(
                {"error": "AI service is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIProviderError:
            return Response(
                {"error": "AI provider is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIStructuredOutputError:
            return Response(
                {"error": "AI returned an invalid story-point estimate."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIResponseError:
            return Response(
                {"error": "AI returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response_serializer = StoryPointEstimationResponseSerializer(data=result)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
