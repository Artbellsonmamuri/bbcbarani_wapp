from rest_framework import serializers
from .models import Media, MediaCategory, MediaUsage


class MediaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaCategory
        fields = '__all__'


class MediaUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaUsage
        fields = '__all__'


class MediaSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_size_human = serializers.CharField(read_only=True)
    thumbnail_url = serializers.CharField(source='get_thumbnail_url', read_only=True)
    usage_instances = MediaUsageSerializer(many=True, read_only=True)

    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ('uploaded_by', 'file_size', 'mime_type', 'width', 'height', 'usage_count', 'last_used')

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class MediaSearchSerializer(serializers.Serializer):
    """Serializer for media search parameters"""
    search = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    media_type = serializers.ChoiceField(choices=Media.MEDIA_TYPES, required=False)
    tags = serializers.CharField(required=False, allow_blank=True)
