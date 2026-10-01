from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService


from ..exceptions import (
    IssueNotFoundException,
    CommentInvalidException,
    CommentNotFoundException,
    ProjectNotFoundException,
    CommentPermissionException,
)

from ..serializers import (
    CommentSerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
    CommentReactionSerializer,
    CommentListQuerySerializer,
)

from ..services.issue_service import IssueService
from ..services.comment_service import CommentService
from ..services.project_service import ProjectService


class IssueCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, issue_id):
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

        query_serializer = CommentListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        comments = CommentService.list_comments(
            issue=issue, **query_serializer.validated_data
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(comments, request)

        serializer = CommentListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

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

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            comment = CommentService.create_comment(
                issue=issue, user=request.user, **serializer.validated_data
            )
        except CommentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = CommentSerializer(comment)

        return Response(
            {
                "message": "Comment created successfully.",
                "comment": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class IssueCommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, slug, project_slug, issue_id, comment_id):
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

        serializer = CommentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            comment = CommentService.update_comment(
                issue=issue,
                comment_id=comment_id,
                user=request.user,
                **serializer.validated_data,
            )
        except CommentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except CommentPermissionException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        response_serializer = CommentSerializer(comment)

        return Response(
            {**response_serializer.data, "message": "Comment updated successfully."},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, slug, project_slug, issue_id, comment_id):
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
            CommentService.delete_comment(
                issue=issue, comment_id=comment_id, user=request.user
            )
        except CommentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except CommentPermissionException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {"message": "Comment deleted successfully."}, status=status.HTTP_200_OK
        )


class IssueCommentReactionView(APIView):

    def put(self, request, slug, project_slug, issue_id, comment_id):
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

        serializer = CommentReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reaction_summary = CommentService.set_reaction(
                issue=issue,
                comment_id=comment_id,
                user=request.user,
                **serializer.validated_data,
            )
        except CommentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"message": "Reaction updated successfully.", "reaction": reaction_summary},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, slug, project_slug, issue_id, comment_id):
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
            CommentService.remove_reaction(
                issue=issue, comment_id=comment_id, user=request.user
            )
        except CommentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except CommentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueCommentReactionSummaryView(APIView):

    def get(self, request, slug, project_slug, issue_id, comment_id):
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
            summary = CommentService.get_reaction_summary(
                issue=issue, comment_id=comment_id, user=request.user
            )
        except CommentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(summary, status=status.HTTP_200_OK)
