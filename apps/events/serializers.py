from rest_framework import serializers
from .models import Event, EventCategory, EventRegistration, EventAttendance


class EventCategorySerializer(serializers.ModelSerializer):
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = EventCategory
        fields = '__all__'

    def get_event_count(self, obj):
        return obj.event_set.filter(status='published').count()


class EventRegistrationSerializer(serializers.ModelSerializer):
    registrant_name = serializers.SerializerMethodField()
    registrant_email = serializers.SerializerMethodField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ('registered_at', 'updated_at')

    def get_registrant_name(self, obj):
        return obj.get_registrant_name()

    def get_registrant_email(self, obj):
        return obj.get_registrant_email()

    def create(self, validated_data):
        request = self.context['request']
        if request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    featured_image_url = serializers.CharField(source='featured_image.file.url', read_only=True)
    registration_count = serializers.IntegerField(read_only=True)
    spots_available = serializers.SerializerMethodField()
    is_registration_open = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('organizer', 'created_at', 'updated_at')

    def get_spots_available(self, obj):
        return obj.spots_available

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class EventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for event lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    featured_image_url = serializers.CharField(source='featured_image.file.url', read_only=True)
    registration_count = serializers.IntegerField(read_only=True)
    spots_available = serializers.SerializerMethodField()
    is_registration_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'short_description', 'category', 'category_name',
            'start_datetime', 'end_datetime', 'location_name', 'is_virtual',
            'featured_image_url', 'organizer_name', 'requires_rsvp',
            'registration_count', 'spots_available', 'is_registration_open',
            'is_featured', 'status'
        ]

    def get_spots_available(self, obj):
        return obj.spots_available
