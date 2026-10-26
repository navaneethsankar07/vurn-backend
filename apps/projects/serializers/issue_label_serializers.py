from rest_framework import serializers

from ..models import Label


class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = ["id", "name", "color"]


class LabelQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)


class AddLabelSerializer(serializers.Serializer):
    label_id = serializers.IntegerField(required=False, min_value=1)
    name = serializers.CharField(required=False, max_length=50)
    color = serializers.CharField(required=False, max_length=7, default="#999999")

    def validate(self, attrs):
        if not attrs.get("label_id") and not attrs.get("name"):
            raise serializers.ValidationError("Either label_id or name is required.")

        if attrs.get("label_id") and attrs.get("name"):
            raise serializers.ValidationError("Provide either label_id or name.")

        return attrs
