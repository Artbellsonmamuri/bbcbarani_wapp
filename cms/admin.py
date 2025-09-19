"""
Bible Baptist Church CMS - Admin Configuration
Complete admin interface for content management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Homepage, Page, Post, Event, Ministry, MediaAsset, HeroSlide

@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    list_display = ('title', 'hero_title', 'published', 'updated_at', 'image_thumbnail')
    list_filter = ('published', 'updated_at')
    search_fields = ('title', 'hero_title', 'welcome_text')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'published')
        }),
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'church_logo')
        }),
        ('Content', {
            'fields': ('welcome_text', 'service_times', 'featured_verse', 'featured_verse_reference')
        }),
        ('Call to Action', {
            'fields': ('call_to_action_text', 'call_to_action_url'),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def image_thumbnail(self, obj):
        if obj.hero_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.hero_image.url)
        return "No image"
    image_thumbnail.short_description = "Image"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'show_in_navigation', 'navigation_order', 'updated_at', 'image_thumbnail')
    list_filter = ('published', 'show_in_navigation', 'updated_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('published', 'show_in_navigation', 'navigation_order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'published')
        }),
        ('Content', {
            'fields': ('content', 'featured_image')
        }),
        ('Navigation', {
            'fields': ('show_in_navigation', 'navigation_order')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def image_thumbnail(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 3px;" />', obj.featured_image.url)
        return "No image"
    image_thumbnail.short_description = "Image"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'is_featured', 'created_at', 'image_thumbnail')
    list_filter = ('published', 'is_featured', 'author', 'created_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('published', 'is_featured')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'published', 'is_featured')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Meta', {
            'fields': ('author', 'tags', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def image_thumbnail(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 3px;" />', obj.featured_image.url)
        return "No image"
    image_thumbnail.short_description = "Image"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'location', 'published', 'registration_required', 'image_thumbnail')
    list_filter = ('published', 'registration_required', 'start_date')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'is_upcoming', 'is_past')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'published')
        }),
        ('Event Details', {
            'fields': ('description', 'featured_image', 'start_date', 'end_date')
        }),
        ('Location', {
            'fields': ('location', 'address')
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_phone', 'contact_email')
        }),
        ('Registration', {
            'fields': ('registration_required', 'registration_url', 'max_attendees'),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('is_upcoming', 'is_past', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def image_thumbnail(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 3px;" />', obj.featured_image.url)
        return "No image"
    image_thumbnail.short_description = "Image"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('title', 'leader_name', 'target_audience', 'published', 'is_active', 'image_thumbnail')
    list_filter = ('published', 'is_active', 'target_audience')
    search_fields = ('title', 'description', 'leader_name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('published', 'is_active')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'published', 'is_active')
        }),
        ('Content', {
            'fields': ('description', 'featured_image', 'target_audience')
        }),
        ('Leadership', {
            'fields': ('leader_name', 'leader_title', 'leader_email', 'leader_phone')
        }),
        ('Meeting Info', {
            'fields': ('meeting_time', 'meeting_location')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def image_thumbnail(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 3px;" />', obj.featured_image.url)
        return "No image"
    image_thumbnail.short_description = "Image"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'file_size_display', 'uploaded_at', 'file_thumbnail')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_at', 'file_size_mb')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'file_type', 'description')
        }),
        ('File', {
            'fields': ('file', 'file_size_mb')
        }),
        ('Meta', {
            'fields': ('uploaded_at', 'uploaded_by'),
            'classes': ('collapse',)
        })
    )
    
    def file_thumbnail(self, obj):
        if obj.file_type == 'image':
            try:
                return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 3px;" />', obj.file.url)
            except:
                pass
        return format_html('<span style="padding: 8px; background: #f0f0f0; border-radius: 3px; font-size: 11px;">{}</span>', obj.file_type.upper())
    file_thumbnail.short_description = "Preview"
    
    def file_size_display(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_display.short_description = "Size"
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'order', 'has_cta_display', 'updated_at', 'image_thumbnail')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'subtitle')
    list_editable = ('published', 'order')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'background_image')
        }),
        ('Call to Action', {
            'fields': ('call_to_action_text', 'call_to_action_url'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('published', 'order')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def image_thumbnail(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" style="width: 60px; height: 35px; object-fit: cover; border-radius: 4px;" />', obj.background_image.url)
        return "No image"
    image_thumbnail.short_description = "Preview"
    
    def has_cta_display(self, obj):
        return "✓" if obj.has_cta else "✗"
    has_cta_display.short_description = "Has CTA"
#    has_cta_display.boolean = True
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Customize admin site headers
admin.site.site_header = "Bible Baptist Church CMS"
admin.site.site_title = "BBC CMS Admin"
admin.site.index_title = "Content Management System"
