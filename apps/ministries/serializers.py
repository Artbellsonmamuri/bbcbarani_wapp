from rest_framework import serializers
from .models import Ministry, MinistryCategory, MinistryMember, MinistryEvent


class MinistryCategorySerializer(serializers.ModelSerializer):
    ministry_count = serializers.SerializerMethodField()

    class Meta:
        model = MinistryCategory
        fields = '__all__'

    def get_ministry_count(self, obj):
        return obj.ministry_set.filter(is_active=True).count()


class MinistryMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = MinistryMember
        fields = '__all__'


class MinistryEventSerializer(serializers.ModelSerializer):
    ministry_name = serializers.CharField(source='ministry.title', read_only=True)
    registration_count = serializers.SerializerMethodField()
    spots_available = serializers.SerializerMethodField()

    class Meta:
        model = MinistryEvent
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def get_registration_count(self, obj):
        return obj.registration_count

    def get_spots_available(self, obj):
        return obj.spots_available


class MinistrySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    leader_name = serializers.CharField(source='leader.get_full_name', read_only=True)
    display_icon = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    carousel_images = serializers.SerializerMethodField()
    upcoming_events = MinistryEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ministry
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def get_display_icon(self, obj):
        return obj.display_icon

    def get_member_count(self, obj):
        return obj.ministry_members.filter(is_active=True).count()

    def get_carousel_images(self, obj):
        return [{'url': img.file.url, 'alt': img.alt_text} for img in obj.carousel_images.all()]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MinistryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for ministry lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    display_icon = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Ministry
        fields = [
            'id', 'title', 'slug', 'short_description', 'category', 'category_name',
            'display_icon', 'member_count', 'featured', 'is_active', 'order'
        ]

    def get_display_icon(self, obj):
        return obj.display_icon

    def get_member_count(self, obj):
        return obj.get_member_count()
