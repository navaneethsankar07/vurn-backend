from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.exceptions import IssueNotFoundException, ProjectNotFoundException
from apps.projects.services.issue_service import IssueService
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService
from apps.projects.services.project_service import ProjectService
from apps.projects.models import Sprint

from .exceptions import (
    AIConfigurationError,
    AIProviderError,
    AIResponseError,
    AIStructuredOutputError,
)
from .serializers import (
    DuplicateDetectionRequestSerializer,
    SprintSummaryRequestSerializer,
    StoryPointEstimationRequestSerializer,
    StoryPointEstimationResponseSerializer,
    TaskBreakdownRequestSerializer,
    TaskBreakdownResponseSerializer,
)
from .services.sprint_summary_service import SprintSummaryService
from .services.task_breakdown_service import TaskBreakdownService
from .services.duplicate_detection_service import DuplicateDetectionService
from .services.story_point_estimation_service import StoryPointEstimationService


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

    def post(self, request):
        request_serializer = StoryPointEstimationRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        issue_id = request_serializer.validated_data["issue_id"]

        try:
            issue = IssueService.get_issue_by_id(issue_id=issue_id)
        except IssueNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        try:
            result = StoryPointEstimationService.estimate(issue=issue)
        except AIConfigurationError:
            return Response(
                {"error": "AI service is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIStructuredOutputError:
            return Response(
                {"error": "AI returned an invalid story-point estimate."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIProviderError:
            return Response(
                {"error": "AI provider is temporarily unavailable."},
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


class DuplicateIssueDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = DuplicateDetectionRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = request_serializer.validated_data

        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=data["organization_slug"]
            )

            project = ProjectService.get_project(
                organization=organization, slug=data["project_slug"]
            )

            result = DuplicateDetectionService.detect(
                user=request.user,
                project_id=project.id,
                title=data["title"],
                description=data.get("description", ""),
                issue_type=data.get("issue_type", ""),
                priority=data.get("priority", "medium"),
            )

        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except AIConfigurationError:
            return Response(
                {"error": "AI service is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIStructuredOutputError:
            return Response(
                {"error": "AI returned an invalid duplicate detection result."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIProviderError:
            return Response(
                {"error": "AI provider is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIResponseError:
            return Response(
                {"error": "AI returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result, status=status.HTTP_200_OK)


class SprintSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = SprintSummaryRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data

        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=data["organization_slug"]
            )

            project = ProjectService.get_project(
                organization=organization, slug=data["project_slug"]
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        sprint = Sprint.objects.filter(id=data["sprint_id"], project=project).first()

        if sprint is None:
            return Response(
                {"error": "Sprint not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            result = SprintSummaryService.generate(sprint=sprint)
        except AIConfigurationError:
            return Response(
                {"error": "AI service is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIStructuredOutputError:
            return Response(
                {"error": "AI returned an invalid sprint summary."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIProviderError:
            return Response(
                {"error": "AI provider is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIResponseError:
            return Response(
                {"error": "AI returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"summary": result}, status=status.HTTP_200_OK)
