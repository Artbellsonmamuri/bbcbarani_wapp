from rest_framework import serializers
from .models import Notification, NotificationPreference, AnnouncementBanner


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    icon = serializers.SerializerMethodField()
    color_class = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('recipient', 'sender', 'created_at', 'read_at', 'email_sent_at', 'sms_sent_at')

    def get_icon(self, obj):
        return obj.get_icon()

    def get_color_class(self, obj):
        return obj.get_color_class()


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class AnnouncementBannerSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_currently_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = AnnouncementBanner
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
