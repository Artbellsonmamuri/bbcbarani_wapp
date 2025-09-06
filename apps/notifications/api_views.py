from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification, NotificationPreference, AnnouncementBanner
from .serializers import (
    NotificationSerializer, NotificationPreferenceSerializer, 
    AnnouncementBannerSerializer
)
from .services import NotificationService

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission for notification access"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'recipient') and obj.recipient == request.user:
            return True
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        return False


class NotificationViewSet(viewsets.ModelViewSet):
    """API ViewSet for notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(recipient=user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all user's notifications as read"""
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({'updated_count': updated})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'count': count})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """API ViewSet for notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnnouncementBannerViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for announcement banners (read-only for public)"""
    serializer_class = AnnouncementBannerSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return AnnouncementBanner.objects.filter(
            is_active=True,
            start_datetime__lte=now,
            end_datetime__gte=now
        )

    def list(self, request, *args, **kwargs):
        """Filter banners based on user"""
        queryset = self.get_queryset()

        # Filter by user targeting
        if request.user.is_authenticated:
            queryset = queryset.filter(
                models.Q(show_to_all_users=True) | 
                models.Q(show_to_members_only=True)
            )
        else:
            queryset = queryset.filter(
                models.Q(show_to_all_users=True) | 
                models.Q(show_to_guests_only=True)
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_notification(request):
    """Send a single notification"""

    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data
    recipient_id = data.get('recipient_id')
    title = data.get('title')
    message = data.get('message')

    if not all([recipient_id, title, message]):
        return Response(
            {'error': 'recipient_id, title, and message are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        recipient = User.objects.get(id=recipient_id)

        service = NotificationService()
        notification = service.create_notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=data.get('notification_type', 'info'),
            sender=request.user,
            action_url=data.get('action_url'),
            action_text=data.get('action_text'),
            priority=data.get('priority', 'normal')
        )

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response(
            {'error': 'Recipient not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_send_notification(request):
    """Send notifications to multiple recipients"""

    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data
    recipient_type = data.get('recipient_type', 'all')
    title = data.get('title')
    message = data.get('message')

    if not all([title, message]):
        return Response(
            {'error': 'title and message are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Determine recipients
    if recipient_type == 'all':
        recipients = User.objects.filter(is_active=True)
    elif recipient_type == 'admins':
        recipients = User.objects.filter(is_staff=True)
    elif recipient_type == 'members':
        recipients = User.objects.filter(is_active=True, is_staff=False)
    elif recipient_type == 'ministry_leads':
        recipients = User.objects.filter(role='ministry_lead')
    else:
        return Response(
            {'error': 'Invalid recipient_type'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = NotificationService()
    notifications = service.bulk_notify(
        recipients=recipients,
        title=title,
        message=message,
        notification_type=data.get('notification_type', 'info'),
        sender=request.user,
        action_url=data.get('action_url'),
        action_text=data.get('action_text'),
        priority=data.get('priority', 'normal')
    )

    return Response({
        'sent_count': len(notifications),
        'recipient_type': recipient_type
    }, status=status.HTTP_201_CREATED)
