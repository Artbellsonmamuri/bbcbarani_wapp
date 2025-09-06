from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib import messages
from .models import SiteTheme, ThemeCustomization, ColorPalette, FontFamily


@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_default', 'preview_image_tag', 'created_by', 'created_at')
    list_filter = ('is_active', 'is_default', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'css_preview')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'preview_image')
        }),
        ('CSS Configuration', {
            'fields': ('css_settings', 'custom_css', 'css_preview')
        }),
        ('Status', {
            'fields': ('is_active', 'is_default')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_theme', 'duplicate_theme']

    def preview_image_tag(self, obj):
        if obj.preview_image:
            return format_html('<img src="{}" style="height: 50px; width: auto;">', obj.preview_image.url)
        return 'No preview'
    preview_image_tag.short_description = 'Preview'

    def css_preview(self, obj):
        if obj.css_settings:
            css_display = ""
            for key, value in obj.css_settings.items():
                css_display += f"<div><strong>{key}:</strong> {value}</div>"
            return mark_safe(css_display)
        return "No CSS settings"
    css_preview.short_description = 'CSS Settings Preview'

    def activate_theme(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Please select exactly one theme to activate.')
            return

        theme = queryset.first()
        theme.activate()
        messages.success(request, f'Theme "{theme.name}" has been activated.')
    activate_theme.short_description = 'Activate selected theme'

    def duplicate_theme(self, request, queryset):
        for theme in queryset:
            new_theme = SiteTheme.objects.create(
                name=f"{theme.name} (Copy)",
                description=f"Copy of {theme.description}",
                css_settings=theme.css_settings.copy(),
                custom_css=theme.custom_css,
                created_by=request.user
            )
        messages.success(request, f'{queryset.count()} theme(s) duplicated.')
    duplicate_theme.short_description = 'Duplicate selected themes'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ColorPalette)
class ColorPaletteAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Brand Colors', {
            'fields': ('primary_color', 'secondary_color', 'accent_color')
        }),
        ('Text Colors', {
            'fields': ('text_color', 'text_light', 'text_muted')
        }),
        ('Background Colors', {
            'fields': ('background_color', 'background_alt')
        }),
        ('Status Colors', {
            'fields': ('success_color', 'warning_color', 'danger_color', 'info_color')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="display: flex; gap: 2px;">'
            '<div style="background-color: {}; width: 20px; height: 20px;"></div>'
            '<div style="background-color: {}; width: 20px; height: 20px;"></div>'
            '<div style="background-color: {}; width: 20px; height: 20px;"></div>'
            '</div>',
            obj.primary_color, obj.secondary_color, obj.accent_color
        )
    color_preview.short_description = 'Colors'


@admin.register(FontFamily)
class FontFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'font_preview', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'font_family')

    fieldsets = (
        ('Font Information', {
            'fields': ('name', 'font_family', 'category', 'google_fonts_url')
        }),
        ('Preview', {
            'fields': ('preview_text',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

    def font_preview(self, obj):
        return format_html(
            '<span style="font-family: {}; font-size: 14px;">{}</span>',
            obj.font_family,
            obj.name
        )
    font_preview.short_description = 'Preview'


@admin.register(ThemeCustomization)
class ThemeCustomizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'is_active', 'updated_at')
    list_filter = ('theme', 'is_active', 'updated_at')
    search_fields = ('user__username', 'theme__name')
    readonly_fields = ('created_at', 'updated_at')
