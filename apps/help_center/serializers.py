from rest_framework import serializers


class HelpTopicListSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    title = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()


class HelpTopicDetailSerializer(HelpTopicListSerializer):
    content = serializers.CharField()
