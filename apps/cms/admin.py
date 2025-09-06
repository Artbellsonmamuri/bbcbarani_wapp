from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ContentSection, WelcomeScreen, ServiceSchedule, HeaderFooter, SEOSettings, ContentRevision


class ContentRevisionInline(admin.TabularInline):
    model = ContentRevision
    extra = 0
    readonly_fields = ('revision_number', 'changed_by', 'change_summary', 'created_at')
    fields = ('revision_number', 'change_summary', 'changed_by', 'created_at')

    def has_add_permission(self, request, obj):
        return False


@admin.register(ContentSection)
class ContentSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'status', 'language', 'featured', 'created_by', 'updated_at', 'preview_link')
    list_filter = ('section_type', 'status', 'language', 'featured', 'created_at')
    search_fields = ('title', 'body', 'meta_title', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('version', 'created_at', 'updated_at', 'created_by', 'updated_by')

    fieldsets = (
        ('Basic Information', {
            'fields': ('section_type', 'title', 'slug', 'excerpt', 'body', 'structured_content')
        }),
        ('Publishing', {
            'fields': ('status', 'featured', 'publish_date', 'order', 'language')
        }),
        ('SEO & Social Media', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Version Control', {
            'fields': ('version', 'parent_version'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ContentRevisionInline]

    def preview_link(self, obj):
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
            obj.version += 1
        else:
            obj.created_by = request.user
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

        # Create revision
        ContentRevision.objects.create(
            content_section=obj,
            revision_number=obj.version,
            title=obj.title,
            body=obj.body,
            structured_content=obj.structured_content,
            changed_by=request.user,
            change_summary=f"Version {obj.version}"
        )


@admin.register(WelcomeScreen)
class WelcomeScreenAdmin(admin.ModelAdmin):
    list_display = ('pastor_name', 'pastor_title', 'welcome_message_preview')
    readonly_fields = ('content_section',)

    fieldsets = (
        ('Welcome Message', {
            'fields': ('welcome_message', 'subtitle', 'cta_text', 'cta_link')
        }),
        ('Pastor Information', {
            'fields': ('pastor_name', 'pastor_title', 'pastor_photo', 'pastor_bio')
        }),
        ('Branding', {
            'fields': ('church_logo', 'carousel_images')
        }),
    )

    def welcome_message_preview(self, obj):
        return obj.welcome_message[:50] + '...' if len(obj.welcome_message) > 50 else obj.welcome_message
    welcome_message_preview.short_description = 'Message Preview'


@admin.register(ServiceSchedule)
class ServiceScheduleAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'day_of_week', 'start_time', 'location_name', 'live_stream_enabled', 'is_active')
    list_filter = ('day_of_week', 'live_stream_enabled', 'is_active')
    ordering = ['order', 'day_of_week', 'start_time']

    fieldsets = (
        ('Service Details', {
            'fields': ('service_name', 'description', 'day_of_week', 'start_time', 'end_time')
        }),
        ('Location', {
            'fields': ('location_name', 'address')
        }),
        ('Live Streaming', {
            'fields': ('live_stream_enabled', 'live_stream_platform', 'live_stream_url')
        }),
        ('Settings', {
            'fields': ('special_notes', 'is_active', 'order')
        }),
    )


@admin.register(HeaderFooter)
class HeaderFooterAdmin(admin.ModelAdmin):
    list_display = ('section', 'updated_at')

    fieldsets = (
        ('Content', {
            'fields': ('section', 'content')
        }),
        ('Header Settings', {
            'fields': ('show_language_switcher', 'show_search'),
            'classes': ('collapse',)
        }),
        ('Footer Information', {
            'fields': ('copyright_text', 'footer_message', 'phone', 'email', 'address'),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'youtube_url', 'instagram_url', 'twitter_url'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_tagline', 'site_description')
        }),
        ('Analytics & Tracking', {
            'fields': ('google_analytics_id', 'google_tag_manager_id'),
            'classes': ('collapse',)
        }),
        ('Site Verification', {
            'fields': ('google_site_verification', 'bing_site_verification'),
            'classes': ('collapse',)
        }),
        ('Social Media Defaults', {
            'fields': ('default_og_image', 'facebook_app_id'),
            'classes': ('collapse',)
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        return not SEOSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
