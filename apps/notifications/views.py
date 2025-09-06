from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Notification, NotificationPreference, AnnouncementBanner
from .forms import NotificationPreferenceForm
from .services import NotificationService


@login_required
def notification_list(request):
    """List user's notifications with filtering"""

    notifications = Notification.objects.filter(recipient=request.user)

    # Filter by read status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)

    # Filter by type
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)

    # Order and paginate
    notifications = notifications.order_by('-created_at')

    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count unread
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
        'filter_type': filter_type,
        'notification_type': notification_type,
    }
    return render(request, 'notifications/list.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read via AJAX"""

    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.mark_as_read()

        return JsonResponse({
            'success': True,
            'is_read': notification.is_read
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_all_read(request):
    """Mark all user's notifications as read"""

    updated = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())

    return JsonResponse({
        'success': True,
        'updated_count': updated
    })


@login_required
def notification_preferences(request):
    """User notification preferences"""

    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your notification preferences have been updated.')
            return redirect('notifications:preferences')
    else:
        form = NotificationPreferenceForm(instance=preferences)

    context = {
        'form': form,
        'preferences': preferences,
    }
    return render(request, 'notifications/preferences.html', context)


def get_notification_count(request):
    """API endpoint for unread notification count"""

    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})

    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return JsonResponse({'count': count})


def get_recent_notifications(request):
    """API endpoint for recent notifications"""

    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]

    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'action_text': notification.action_text,
            'icon': notification.get_icon(),
            'color_class': notification.get_color_class(),
        })

    return JsonResponse({'notifications': data})


def get_active_banners(request):
    """Get active announcement banners for current user"""

    banners = AnnouncementBanner.objects.filter(
        is_active=True
    )

    # Filter by scheduling
    now = timezone.now()
    banners = banners.filter(
        Q(start_datetime__isnull=True) | Q(start_datetime__lte=now),
        Q(end_datetime__isnull=True) | Q(end_datetime__gte=now)
    )

    # Filter by user targeting
    if request.user.is_authenticated:
        banners = banners.filter(
            Q(show_to_all_users=True) | Q(show_to_members_only=True)
        )
    else:
        banners = banners.filter(
            Q(show_to_all_users=True) | Q(show_to_guests_only=True)
        )

    data = []
    for banner in banners:
        data.append({
            'id': banner.id,
            'title': banner.title,
            'message': banner.message,
            'banner_type': banner.banner_type,
            'position': banner.position,
            'is_dismissible': banner.is_dismissible,
            'action_text': banner.action_text,
            'action_url': banner.action_url,
            'action_opens_new_tab': banner.action_opens_new_tab,
        })

    return JsonResponse({'banners': data})


@staff_member_required
def notification_dashboard(request):
    """Admin dashboard for notifications"""

    # Statistics
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    active_banners = AnnouncementBanner.objects.filter(is_active=True).count()

    # Recent notifications
    recent_notifications = Notification.objects.order_by('-created_at')[:10]

    # Notification stats by type
    notification_stats = Notification.objects.values('notification_type').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'active_banners': active_banners,
        'recent_notifications': recent_notifications,
        'notification_stats': notification_stats,
    }
    return render(request, 'notifications/admin/dashboard.html', context)


@staff_member_required
def send_custom_notification(request):
    """Send custom notification to selected users"""

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type', 'info')
        recipient_type = request.POST.get('recipient_type', 'all')

        # Determine recipients
        if recipient_type == 'all':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipients = User.objects.filter(is_active=True)
        elif recipient_type == 'admins':
            recipients = User.objects.filter(is_staff=True)
        elif recipient_type == 'members':
            recipients = User.objects.filter(is_active=True, is_staff=False)
        else:
            recipients = User.objects.none()

        # Send notifications
        notification_service = NotificationService()
        sent_count = 0

        for recipient in recipients:
            notification_service.create_notification(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                sender=request.user
            )
            sent_count += 1

        messages.success(request, f'Sent {sent_count} notifications successfully.')
        return redirect('notifications:admin_dashboard')

    return render(request, 'notifications/admin/send_notification.html')
