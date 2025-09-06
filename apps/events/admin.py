from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count
from .models import Event, EventCategory, EventRegistration, EventAttendance


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    fields = ('get_registrant_name', 'number_of_attendees', 'status', 'payment_status', 'registered_at')
    readonly_fields = ('get_registrant_name', 'registered_at')

    def get_registrant_name(self, obj):
        return obj.get_registrant_name()
    get_registrant_name.short_description = 'Registrant'


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview', 'icon', 'event_count', 'is_active', 'order')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def color_preview(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'

    def event_count(self, obj):
        return obj.event_set.count()
    event_count.short_description = 'Events'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_datetime', 'category', 'status', 'registration_info', 'is_featured', 'organizer')
    list_filter = ('status', 'category', 'is_featured', 'requires_rsvp', 'is_virtual', 'start_datetime')
    search_fields = ('title', 'description', 'location_name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('registration_count', 'spots_available', 'created_at', 'updated_at')
    filter_horizontal = ('co_organizers', 'gallery_images')
    date_hierarchy = 'start_datetime'

    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'slug', 'short_description', 'description', 'featured_image', 'category')
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime', 'timezone')
        }),
        ('Location', {
            'fields': ('location_name', 'address', 'is_virtual', 'virtual_link')
        }),
        ('Organization', {
            'fields': ('organizer', 'co_organizers', 'contact_person', 'contact_email', 'contact_phone')
        }),
        ('Registration & RSVP', {
            'fields': ('requires_rsvp', 'max_attendees', 'registration_deadline', 'allow_guest_registration', 'registration_fee')
        }),
        ('Media', {
            'fields': ('gallery_images',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('status', 'is_featured', 'is_recurring', 'recurrence_pattern')
        }),
        ('Notifications', {
            'fields': ('send_reminders', 'reminder_schedule'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('registration_count', 'spots_available'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [EventRegistrationInline]
    actions = ['mark_as_completed', 'cancel_events', 'feature_events']

    def registration_info(self, obj):
        if obj.requires_rsvp:
            return f"{obj.registration_count}/{obj.max_attendees or '∞'}"
        return "No RSVP"
    registration_info.short_description = 'Registrations'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        messages.success(request, f'{updated} events marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'

    def cancel_events(self, request, queryset):
        updated = queryset.update(status='cancelled')
        messages.success(request, f'{updated} events cancelled.')
    cancel_events.short_description = 'Cancel events'

    def feature_events(self, request, queryset):
        updated = queryset.update(is_featured=True)
        messages.success(request, f'{updated} events featured.')
    feature_events.short_description = 'Feature events'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.organizer = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'get_registrant_name', 'number_of_attendees', 'status', 'payment_status', 'registered_at')
    list_filter = ('status', 'payment_status', 'event__category', 'registered_at')
    search_fields = ('event__title', 'guest_name', 'guest_email', 'user__username')
    readonly_fields = ('total_cost', 'registered_at', 'updated_at')

    fieldsets = (
        ('Registration Details', {
            'fields': ('event', 'user', 'guest_name', 'guest_email', 'guest_phone')
        }),
        ('Attendee Information', {
            'fields': ('number_of_attendees', 'attendee_names', 'dietary_restrictions', 'special_requirements')
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_status', 'payment_amount', 'total_cost')
        }),
        ('Check-in', {
            'fields': ('checked_in_at', 'checked_in_by'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('registration_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('registered_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirm_registrations', 'mark_as_attended', 'send_reminder_emails']

    def confirm_registrations(self, request, queryset):
        updated = queryset.update(status='confirmed')
        messages.success(request, f'{updated} registrations confirmed.')
    confirm_registrations.short_description = 'Confirm registrations'

    def mark_as_attended(self, request, queryset):
        updated = queryset.update(status='attended')
        messages.success(request, f'{updated} registrations marked as attended.')
    mark_as_attended.short_description = 'Mark as attended'


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'get_attendee_name', 'checked_in_at', 'checked_in_by')
    list_filter = ('event', 'checked_in_at')
    search_fields = ('event__title', 'registration__guest_name', 'walk_in_name')

    def get_attendee_name(self, obj):
        if obj.registration:
            return obj.registration.get_registrant_name()
        return obj.walk_in_name
    get_attendee_name.short_description = 'Attendee'
