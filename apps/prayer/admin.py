from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from .models import (
    PrayerRequest, PrayerCategory, PrayerResponse, 
    PrayerTeam, PrayerWall
)


class PrayerResponseInline(admin.TabularInline):
    model = PrayerResponse
    extra = 0
    fields = ('message', 'is_public', 'is_internal', 'responder', 'created_at')
    readonly_fields = ('responder', 'created_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.responder = request.user
        super().save_model(request, obj, form, change)


@admin.register(PrayerCategory)
class PrayerCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'is_public', 'order', 'request_count')
    list_editable = ('order', 'is_public')
    list_filter = ('is_public',)
    search_fields = ('name', 'description')
    ordering = ['order', 'name']

    def request_count(self, obj):
        return obj.prayerrequest_set.count()
    request_count.short_description = 'Requests'


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'get_requester_name', 'category', 'status', 'privacy_level', 
        'urgent', 'submitted_at', 'assigned_to', 'status_badge'
    )
    list_filter = ('status', 'privacy_level', 'urgent', 'category', 'submitted_at', 'assigned_to')
    search_fields = ('subject', 'message', 'requester_name', 'email', 'user__username')
    readonly_fields = ('submitted_at', 'updated_at', 'user')
    date_hierarchy = 'submitted_at'

    fieldsets = (
        ('Request Information', {
            'fields': ('category', 'subject', 'message', 'privacy_level')
        }),
        ('Requester Details', {
            'fields': ('user', 'requester_name', 'email', 'phone')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'urgent', 'assigned_to', 'share_with_prayer_team')
        }),
        ('Follow-up', {
            'fields': ('follow_up_date', 'follow_up_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at', 'reviewed_at', 'answered_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [PrayerResponseInline]
    actions = ['mark_as_reviewing', 'mark_as_praying', 'mark_as_answered', 'assign_to_me']

    def status_badge(self, obj):
        colors = {
            'new': 'danger',
            'reviewing': 'warning', 
            'approved': 'info',
            'praying': 'primary',
            'answered': 'success',
            'archived': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def mark_as_reviewing(self, request, queryset):
        updated = queryset.update(status='reviewing', reviewed_at=timezone.now())
        messages.success(request, f'{updated} prayer requests marked as under review.')
    mark_as_reviewing.short_description = 'Mark as reviewing'

    def mark_as_praying(self, request, queryset):
        updated = queryset.update(status='praying')
        messages.success(request, f'{updated} prayer requests marked as being prayed for.')
    mark_as_praying.short_description = 'Mark as being prayed for'

    def mark_as_answered(self, request, queryset):
        updated = queryset.update(status='answered', answered_at=timezone.now())
        messages.success(request, f'{updated} prayer requests marked as answered.')
    mark_as_answered.short_description = 'Mark as answered'

    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        messages.success(request, f'{updated} prayer requests assigned to you.')
    assign_to_me.short_description = 'Assign to me'


@admin.register(PrayerResponse)
class PrayerResponseAdmin(admin.ModelAdmin):
    list_display = ('prayer_request', 'responder', 'is_public', 'is_internal', 'created_at')
    list_filter = ('is_public', 'is_internal', 'shared_with_prayer_team', 'created_at')
    search_fields = ('prayer_request__subject', 'message', 'responder__username')
    autocomplete_fields = ['prayer_request', 'responder']
    readonly_fields = ('created_at',)


@admin.register(PrayerTeam)
class PrayerTeamAdmin(admin.ModelAdmin):
    list_display = ('user', 'team_role', 'is_active', 'email_notifications', 'joined_date')
    list_filter = ('is_active', 'email_notifications', 'urgent_notifications', 'joined_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'team_role')
    autocomplete_fields = ['user']

    fieldsets = (
        ('Team Member Info', {
            'fields': ('user', 'team_role', 'specializations')
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'urgent_notifications', 'daily_digest')
        }),
        ('Permissions', {
            'fields': ('is_active', 'can_respond_to_requests')
        }),
    )


@admin.register(PrayerWall)
class PrayerWallAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author_name', 'is_approved', 'is_featured', 'submitted_at')
    list_filter = ('is_approved', 'is_featured', 'submitted_at')
    search_fields = ('title', 'content', 'author_name', 'author__username')
    readonly_fields = ('submitted_at', 'approved_at')

    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'content', 'related_prayer_request')
        }),
        ('Author Information', {
            'fields': ('author', 'author_name')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_featured', 'approved_by', 'approved_at')
        }),
    )

    actions = ['approve_posts', 'feature_posts']

    def approve_posts(self, request, queryset):
        updated = queryset.update(
            is_approved=True, 
            approved_by=request.user,
            approved_at=timezone.now()
        )
        messages.success(request, f'{updated} prayer wall posts approved.')
    approve_posts.short_description = 'Approve selected posts'

    def feature_posts(self, request, queryset):
        updated = queryset.update(is_featured=True)
        messages.success(request, f'{updated} prayer wall posts featured.')
    feature_posts.short_description = 'Feature selected posts'
