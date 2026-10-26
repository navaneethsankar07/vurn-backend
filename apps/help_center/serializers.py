from rest_framework import serializers


class HelpTopicListSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    title = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()


class HelpTopicDetailSerializer(HelpTopicListSerializer):
    content = serializers.CharField()


class HelpArticleListSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    title = serializers.CharField()
    category = serializers.CharField()
    description = serializers.CharField()
    read_time_minutes = serializers.IntegerField()


class HelpArticleDetailSerializer(HelpArticleListSerializer):
    content = serializers.CharField()


class FAQSerializer(serializers.Serializer):
    id = serializers.SlugField()
    question = serializers.CharField()
    answer = serializers.CharField()
