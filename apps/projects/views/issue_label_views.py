from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService

from ..exceptions import (
    LabelInvalidException,
    IssueNotFoundException,
    LabelNotFoundException,
    ProjectNotFoundException,
)

from ..serializers import (
    LabelSerializer,
    AddLabelSerializer,
    LabelQuerySerializer,
    LabelQuerySerializer,
)

from ..services.issue_service import IssueService
from ..services.label_service import LabelService
from ..services.project_service import ProjectService


class IssueLabelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )
            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        query_serializer = LabelQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        labels = LabelService.list_labels(
            project=project, **query_serializer.validated_data
        )

        response_serializer = LabelSerializer(labels, many=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

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

        serializer = AddLabelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            label = LabelService.add_label(
                project=project, issue=issue, **serializer.validated_data
            )
        except LabelNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except LabelInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = LabelSerializer(label)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class IssueLabelDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, slug, project_slug, issue_id, label_id):
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
            LabelService.remove_label(project=project, issue=issue, label_id=label_id)
        except LabelNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"message": "Label removed successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
