from rest_framework import serializers

from ..models import Document, DocumentFolder, ProjectTag


class DocumentFolderQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)


class DocumentFolderSerializer(serializers.ModelSerializer):
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = DocumentFolder
        fields = [
            "id",
            "name",
            "created_by_id",
            "created_by_name",
            "created_at",
            "updated_at",
        ]


class DocumentFolderCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Folder name cannot be empty.")

        return value


class DocumentFolderUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Folder name cannot be empty.")

        return value


class DocumentQuerySerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(required=False, min_value=1)
    search = serializers.CharField(required=False, allow_blank=True)
    sort = serializers.ChoiceField(
        choices=(
            "updated_desc",
            "updated_asc",
            "created_desc",
            "created_asc",
            "title_asc",
            "title_desc",
        ),
        required=False,
        default="updated_desc",
    )


class DocumentSerializer(serializers.ModelSerializer):
    folder_id = serializers.IntegerField(source="folder.id", read_only=True)
    folder_name = serializers.CharField(source="folder.name", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "folder_id",
            "folder_name",
            "title",
            "created_by_id",
            "created_by_name",
            "current_version",
            "created_at",
            "updated_at",
        ]


class DocumentCreateSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Document title cannot be empty.")

        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Document content cannot be empty.")

        return value


class DocumentDetailSerializer(serializers.ModelSerializer):
    folder_id = serializers.IntegerField(source="folder.id", read_only=True)
    folder_name = serializers.CharField(source="folder.name", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "folder_id",
            "folder_name",
            "title",
            "content",
            "created_by_id",
            "created_by_name",
            "current_version",
            "created_at",
            "updated_at",
        ]


class DocumentUpdateSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(required=False, min_value=1)
    title = serializers.CharField(max_length=255, required=False)
    content = serializers.CharField(required=False)

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Document title cannot be empty.")

        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Document content cannot be empty.")

        return value


class ProjectTagCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Tag name cannot be empty.")

        return value


class ProjectTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTag
        fields = ["id", "name", "created_at"]


class ProjectTagQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
