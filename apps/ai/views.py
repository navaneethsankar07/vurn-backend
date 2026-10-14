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
from apps.integrations.models import GitRepository
from backend.apps.ai.services.wallet_service import OrganizationAIWalletService

from .exceptions import (
    AIConfigurationError,
    AIProviderError,
    AIResponseError,
    AIStructuredOutputError,
    InsufficientAICreditsError,
)
from .serializers import (
    DuplicateDetectionRequestSerializer,
    ReleaseNotesRequestSerializer,
    SprintSummaryRequestSerializer,
    StoryPointEstimationRequestSerializer,
    StoryPointEstimationResponseSerializer,
    TaskBreakdownRequestSerializer,
    TaskBreakdownResponseSerializer,
)
from .services.release_notes_service import ReleaseNotesService
from .services.sprint_summary_service import SprintSummaryService
from .services.task_breakdown_service import TaskBreakdownService
from .services.duplicate_detection_service import DuplicateDetectionService
from .services.story_point_estimation_service import StoryPointEstimationService


import logging

logger = logging.getLogger(__name__)


class TaskBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = TaskBreakdownRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        validated_data = request_serializer.validated_data
        organization_slug = validated_data.pop("organization_slug")

        try:
            organization = OrganizationService.get_organization_by_slug(
                slug=organization_slug
            )

            result = TaskBreakdownService.generate_breakdown(**validated_data)

        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
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

        try:
            OrganizationAIWalletService.consume_credits(
                organization=organization, user=request.user, feature="task_breakdown"
            )
        except InsufficientAICreditsError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_402_PAYMENT_REQUIRED
            )

        return Response(response_serializer.validated_data, status=status.HTTP_200_OK)


class StoryPointEstimationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = StoryPointEstimationRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        validated_data = request_serializer.validated_data
        issue_id = validated_data["issue_id"]
        organization_slug = validated_data["organization_slug"]

        try:
            organization = OrganizationService.get_organization_by_slug(
                slug=organization_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

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

        try:
            OrganizationAIWalletService.consume_credits(
                organization=organization,
                user=request.user,
                feature="story_point_estimation",
            )
        except InsufficientAICreditsError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_402_PAYMENT_REQUIRED
            )

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

        try:
            OrganizationAIWalletService.consume_credits(
                organization=organization,
                user=request.user,
                feature="duplicate_issue_detection",
            )
        except InsufficientAICreditsError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_402_PAYMENT_REQUIRED
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

        try:
            OrganizationAIWalletService.consume_credits(
                organization=organization, user=request.user, feature="sprint_summary"
            )
        except InsufficientAICreditsError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_402_PAYMENT_REQUIRED
            )

        return Response({"summary": result}, status=status.HTTP_200_OK)


class ReleaseNotesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = ReleaseNotesRequestSerializer(data=request.data)
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

        repository = GitRepository.objects.filter(
            id=data["repository_id"],
            integration__project=project,
            integration__status="active",
        ).first()

        if repository is None:
            return Response(
                {"error": "Repository not found or not connected."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = ReleaseNotesService.generate(
                repository=repository,
                start_date=data["start_date"],
                end_date=data["end_date"],
            )
        except AIConfigurationError:
            return Response(
                {"error": "AI service is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIStructuredOutputError:
            logger.exception("AI release notes structured output failed")
            return Response(
                {"error": "AI returned invalid release notes."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIProviderError:
            logger.exception("AI release notes provider request failed")
            return Response(
                {"error": "AI provider is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except AIResponseError:
            logger.exception("AI release notes response processing failed")
            return Response(
                {"error": "AI returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result, status=status.HTTP_200_OK)
