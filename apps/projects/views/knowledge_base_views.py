from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shared.utils.pagination import StandardPagination
from apps.organizations.exceptions import OrganizationNotFoundException
from apps.organizations.services.organization_service import OrganizationService


from ..serializers import (
    DocumentSerializer,
    ProjectTagSerializer,
    DocumentQuerySerializer,
    DocumentFolderSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    DocumentDetailSerializer,
    ProjectTagQuerySerializer,
    ProjectTagCreateSerializer,
    DocumentFolderQuerySerializer,
    DocumentFolderCreateSerializer,
    DocumentFolderUpdateSerializer,
)

from ..exceptions import (
    DocumentFolderInvalidException,
    DocumentFolderNotFoundException,
    ProjectNotFoundException,
    DocumentInvalidException,
    DocumentNotFoundException,
    ProjectPermissionDeniedException,
    DocumentFolderAlreadyExistsException,
    ProjectTagAlreadyExistsException,
)

from ..services.project_service import ProjectService
from ..services.project_tag_service import ProjectTagService
from ..services.project_access_service import ProjectAccessService
from ..services.document_folder_service import DocumentFolderService
from ..services.document_service import DocumentService, DocumentTagService


class DocumentFolderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_view_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        query_serializer = DocumentFolderQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        folders = DocumentFolderService.list_folders(
            project=project, **query_serializer.validated_data
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(folders, request)

        serializer = DocumentFolderSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = DocumentFolderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            folder = DocumentFolderService.create_folder(
                project=project, user=request.user, **serializer.validated_data
            )
        except DocumentFolderAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": folder.id, "message": "Document folder created successfully."},
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request, slug, project_slug, folder_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = DocumentFolderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            folder = DocumentFolderService.update_folder(
                project=project, folder_id=folder_id, **serializer.validated_data
            )
        except DocumentFolderNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except DocumentFolderAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": folder.id,
                "name": folder.name,
                "message": "Document folder updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, slug, project_slug, folder_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        try:
            DocumentFolderService.delete_folder(project=project, folder_id=folder_id)
        except DocumentFolderNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except DocumentFolderInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Document folder deleted successfully."},
            status=status.HTTP_200_OK,
        )


class DocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_view_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        query_serializer = DocumentQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        documents = DocumentService.list_documents(
            project=project, **query_serializer.validated_data
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(documents, request)

        serializer = DocumentSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            document = DocumentService.create_document(
                project=project, user=request.user, **serializer.validated_data
            )
        except DocumentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": document.id, "message": "Document created successfully."},
            status=status.HTTP_201_CREATED,
        )


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, document_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_view_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        try:
            document = DocumentService.get_document(
                project=project, document_id=document_id
            )
        except DocumentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentDetailSerializer(document)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, slug, project_slug, document_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = DocumentUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            document = DocumentService.update_document(
                project=project, document_id=document_id, **serializer.validated_data
            )
        except DocumentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except DocumentInvalidException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": document.id, "message": "Document updated successfully."},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, slug, project_slug, document_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        try:
            DocumentService.delete_document(project=project, document_id=document_id)
        except DocumentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"message": "Document deleted successfully."}, status=status.HTTP_200_OK
        )


class DocumentTagView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_view_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        query_serializer = ProjectTagQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        tags = ProjectTagService.list_tags(
            project=project, **query_serializer.validated_data
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(tags, request)

        serializer = ProjectTagSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug, project_slug):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_edit_access(
                project=project, user=request.user
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectTagCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tag = ProjectTagService.create_tag(
                project=project, **serializer.validated_data
            )
        except ProjectTagAlreadyExistsException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": tag.id,
                "name": tag.name,
                "message": "Document tag created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class DocumentTagSuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, project_slug, document_id):
        try:
            organization = OrganizationService.get_user_organization(
                user=request.user, slug=slug
            )

            project = ProjectService.get_project(
                organization=organization, slug=project_slug
            )

            ProjectAccessService.validate_knowledge_base_view_access(
                project=project, user=request.user
            )

            document = DocumentService.get_document(
                project=project, document_id=document_id
            )
        except OrganizationNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except DocumentNotFoundException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProjectPermissionDeniedException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        tags = DocumentTagService.get_suggestions(project=project, document=document)

        serializer = ProjectTagSerializer(tags, many=True)

        return Response({"tags": serializer.data}, status=status.HTTP_200_OK)
