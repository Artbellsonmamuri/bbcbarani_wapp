from rest_framework import serializers
from .models import PrayerRequest, PrayerCategory, PrayerResponse, PrayerWall, PrayerTeam


class PrayerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerCategory
        fields = '__all__'


class PrayerResponseSerializer(serializers.ModelSerializer):
    responder_name = serializers.CharField(source='responder.get_full_name', read_only=True)

    class Meta:
        model = PrayerResponse
        fields = '__all__'
        read_only_fields = ('responder', 'created_at')

    def create(self, validated_data):
        validated_data['responder'] = self.context['request'].user
        return super().create(validated_data)


class PrayerRequestSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    requester_display_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    responses = PrayerResponseSerializer(many=True, read_only=True)

    class Meta:
        model = PrayerRequest
        fields = '__all__'
        read_only_fields = ('user', 'submitted_at', 'updated_at', 'reviewed_at', 'answered_at')

    def get_requester_display_name(self, obj):
        return obj.get_requester_name()

    def create(self, validated_data):
        # Associate with user if authenticated
        request = self.context['request']
        if request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class PrayerWallSerializer(serializers.ModelSerializer):
    author_display_name = serializers.SerializerMethodField()

    class Meta:
        model = PrayerWall
        fields = '__all__'
        read_only_fields = ('author', 'submitted_at', 'approved_at', 'approved_by')

    def get_author_display_name(self, obj):
        return obj.get_author_name()

    def create(self, validated_data):
        request = self.context['request']
        if request.user.is_authenticated:
            validated_data['author'] = request.user
        return super().create(validated_data)


class PrayerTeamSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = PrayerTeam
        fields = '__all__'
