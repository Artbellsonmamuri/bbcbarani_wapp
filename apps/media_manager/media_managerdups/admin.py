from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.utils.safestring import mark_safe
from .models import (
    MediaFolder, MediaFile, MediaCollection, MediaCollectionItem,
    MediaUsage, MediaDownload
)


class MediaCollectionItemInline(admin.TabularInline):
    model = MediaCollectionItem
    extra = 0
    ordering = ('order',)


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'file_count', 'is_public', 'created_by', 'created_at')
    list_filter = ('is_public', 'created_at', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('allowed_users',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Permissions', {
            'fields': ('is_public', 'allowed_users')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def file_count(self, obj):
        return obj.files.count()
    file_count.short_description = 'Files'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'media_type', 'file_size_display', 'usage_count', 'uploaded_by', 'created_at')
    list_filter = ('media_type', 'is_public', 'is_featured', 'license_type', 'created_at', 'folder')
    search_fields = ('title', 'description', 'original_filename', 'tags')
    readonly_fields = ('file_size', 'mime_type', 'width', 'height', 'usage_count', 'last_used', 'created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'file', 'folder')
        }),
        ('File Details', {
            'fields': ('original_filename', 'file_size', 'mime_type', 'media_type'),
            'classes': ('collapse',)
        }),
        ('Image Details', {
            'fields': ('width', 'height', 'alt_text', 'caption'),
            'classes': ('collapse',)
        }),
        ('Organization', {
            'fields': ('tags', 'is_public', 'is_featured')
        }),
        ('Copyright & Licensing', {
            'fields': ('copyright_info', 'license_type'),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'last_used'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.is_image and obj.file:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.file.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 12px;">{}</div>',
            obj.media_type.upper()
        )
    thumbnail_preview.short_description = 'Preview'

    def file_size_display(self, obj):
        return obj.formatted_file_size
    file_size_display.short_description = 'Size'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['mark_as_featured', 'mark_as_public', 'mark_as_private']

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} files marked as featured.')
    mark_as_featured.short_description = 'Mark as featured'

    def mark_as_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} files marked as public.')
    mark_as_public.short_description = 'Mark as public'

    def mark_as_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} files marked as private.')
    mark_as_private.short_description = 'Mark as private'


@admin.register(MediaCollection)
class MediaCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'media_count', 'is_public', 'is_featured', 'created_by', 'created_at')
    list_filter = ('is_public', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MediaCollectionItemInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'cover_image')
        }),
        ('Settings', {
            'fields': ('is_public', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def media_count(self, obj):
        return obj.media_files.count()
    media_count.short_description = 'Media Files'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MediaUsage)
class MediaUsageAdmin(admin.ModelAdmin):
    list_display = ('media_file', 'content_type', 'content_title', 'usage_context', 'is_active', 'created_at')
    list_filter = ('content_type', 'usage_context', 'is_active', 'created_at')
    search_fields = ('media_file__title', 'content_title')
    readonly_fields = ('created_at', 'last_checked')

    fieldsets = (
        ('Media Reference', {
            'fields': ('media_file',)
        }),
        ('Content Information', {
            'fields': ('content_type', 'content_id', 'content_title', 'content_url', 'usage_context')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'last_checked')
        }),
    )


@admin.register(MediaDownload)
class MediaDownloadAdmin(admin.ModelAdmin):
    list_display = ('media_file', 'downloaded_by', 'ip_address', 'downloaded_at')
    list_filter = ('downloaded_at', 'media_file__media_type')
    search_fields = ('media_file__title', 'downloaded_by__username', 'ip_address')
    readonly_fields = ('downloaded_at',)

    fieldsets = (
        ('Download Information', {
            'fields': ('media_file', 'downloaded_by', 'downloaded_at')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'referer'),
            'classes': ('collapse',)
        }),
    )
