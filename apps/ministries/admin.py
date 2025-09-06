from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Ministry, MinistryCategory, MinistryMember, MinistryEvent


class MinistryMemberInline(admin.TabularInline):
    model = MinistryMember
    extra = 0
    fields = ('user', 'role', 'skills', 'is_active')
    autocomplete_fields = ['user']


class MinistryEventInline(admin.TabularInline):
    model = MinistryEvent
    extra = 0
    fields = ('title', 'start_datetime', 'requires_registration', 'is_public')
    readonly_fields = ('created_at',)


@admin.register(MinistryCategory)
class MinistryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'order', 'ministry_count')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    ordering = ['order', 'name']

    def ministry_count(self, obj):
        return obj.ministry_set.count()
    ministry_count.short_description = 'Ministries'


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'leader', 'icon_preview', 'member_count', 'is_active', 'featured', 'created_at')
    list_filter = ('category', 'is_active', 'featured', 'requires_membership', 'created_at')
    search_fields = ('title', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'member_count')
    filter_horizontal = ('carousel_images', 'co_leaders')
    autocomplete_fields = ['leader', 'custom_icon']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'short_description', 'full_description')
        }),
        ('Visual Elements', {
            'fields': ('icon_type', 'font_icon', 'custom_icon', 'carousel_images')
        }),
        ('Leadership', {
            'fields': ('leader', 'co_leaders')
        }),
        ('Contact & Meeting Info', {
            'fields': ('contact_email', 'contact_phone', 'meeting_location', 'meeting_schedule'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'featured', 'allow_public_contact', 'requires_membership', 'order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('member_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [MinistryMemberInline, MinistryEventInline]

    def icon_preview(self, obj):
        icon = obj.display_icon
        if icon['type'] == 'image':
            return format_html('<img src="{}" style="height: 30px; width: 30px;" alt="{}">', 
                             icon['url'], icon.get('alt', ''))
        else:
            return format_html('<i class="{}"></i>', icon['class'])
    icon_preview.short_description = 'Icon'

    def member_count(self, obj):
        return obj.ministry_members.filter(is_active=True).count()
    member_count.short_description = 'Active Members'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MinistryMember)
class MinistryMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'ministry', 'role', 'joined_date', 'is_active')
    list_filter = ('ministry', 'role', 'is_active', 'joined_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'ministry__title')
    autocomplete_fields = ['user', 'ministry']
    date_hierarchy = 'joined_date'


@admin.register(MinistryEvent)
class MinistryEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'ministry', 'start_datetime', 'registration_count', 'is_public', 'is_featured')
    list_filter = ('ministry', 'is_public', 'is_featured', 'requires_registration', 'start_datetime')
    search_fields = ('title', 'description', 'ministry__title')
    autocomplete_fields = ['ministry', 'contact_person', 'featured_image']
    date_hierarchy = 'start_datetime'

    fieldsets = (
        ('Event Details', {
            'fields': ('ministry', 'title', 'description', 'featured_image')
        }),
        ('Schedule & Location', {
            'fields': ('start_datetime', 'end_datetime', 'location')
        }),
        ('Registration', {
            'fields': ('requires_registration', 'max_attendees', 'registration_deadline')
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Settings', {
            'fields': ('is_public', 'is_featured')
        }),
    )

    def registration_count(self, obj):
        return obj.registration_count if hasattr(obj, 'registration_count') else 0
    registration_count.short_description = 'Registrations'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
