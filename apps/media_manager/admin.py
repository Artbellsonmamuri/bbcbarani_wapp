from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Media, MediaCategory, MediaUsage


@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'file_preview', 'file_size_human', 'category', 'uploaded_by', 'usage_count', 'is_public', 'created_at')
    list_filter = ('media_type', 'category', 'is_public', 'uploaded_by', 'created_at')
    search_fields = ('title', 'description', 'tags', 'original_filename')
    readonly_fields = ('file_size', 'mime_type', 'width', 'height', 'usage_count', 'last_used', 'file_preview', 'usage_list')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'file', 'file_preview')
        }),
        ('Organization', {
            'fields': ('category', 'tags', 'is_public')
        }),
        ('Image Details', {
            'fields': ('alt_text', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('File Information', {
            'fields': ('media_type', 'file_size', 'mime_type', 'original_filename'),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'last_used', 'usage_list'),
            'classes': ('collapse',)
        }),
    )

    def file_preview(self, obj):
        if obj.is_image and obj.file:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px;">',
                obj.file.url
            )
        elif obj.is_video and obj.file:
            return format_html(
                '<video controls style="max-width: 150px; max-height: 150px;"><source src="{}"></video>',
                obj.file.url
            )
        elif obj.file:
            return format_html('<a href="{}" target="_blank">Download File</a>', obj.file.url)
        return '-'
    file_preview.short_description = 'Preview'

    def usage_list(self, obj):
        usage_instances = obj.usage_instances.all()[:5]
        if usage_instances:
            usage_html = '<ul>'
            for usage in usage_instances:
                usage_html += f'<li>{usage.content_type} #{usage.object_id} ({usage.field_name})</li>'
            usage_html += '</ul>'
            if obj.usage_instances.count() > 5:
                usage_html += f'<p>... and {obj.usage_instances.count() - 5} more</p>'
            return mark_safe(usage_html)
        return 'Not used yet'
    usage_list.short_description = 'Used In'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MediaUsage)
class MediaUsageAdmin(admin.ModelAdmin):
    list_display = ('media', 'content_type', 'object_id', 'field_name', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('media__title', 'content_type')
    readonly_fields = ('created_at',)
