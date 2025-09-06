from rest_framework import serializers
from .models import ContentSection, WelcomeScreen, ServiceSchedule, HeaderFooter, SEOSettings, ContentRevision


class ContentSectionSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = ContentSection
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'created_at', 'updated_at', 'version')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        instance.version += 1
        return super().update(instance, validated_data)


class WelcomeScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = WelcomeScreen
        fields = '__all__'


class ServiceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSchedule
        fields = '__all__'


class HeaderFooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeaderFooter
        fields = '__all__'


class SEOSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOSettings
        fields = '__all__'


class ContentRevisionSerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = ContentRevision
        fields = '__all__'
        read_only_fields = ('changed_by', 'created_at')
