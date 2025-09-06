from rest_framework import serializers
from .models import SiteTheme, ColorPalette, FontFamily, ThemeCustomization


class ColorPaletteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorPalette
        fields = '__all__'


class FontFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = FontFamily
        fields = '__all__'


class SiteThemeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    compiled_css = serializers.SerializerMethodField()
    css_variables = serializers.SerializerMethodField()

    class Meta:
        model = SiteTheme
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def get_compiled_css(self, obj):
        return obj.get_compiled_css()

    def get_css_variables(self, obj):
        return obj.get_css_variables()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ThemeCustomizationSerializer(serializers.ModelSerializer):
    theme_name = serializers.CharField(source='theme.name', read_only=True)

    class Meta:
        model = ThemeCustomization
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
