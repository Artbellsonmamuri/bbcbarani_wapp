from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from .models import PrayerRequest, PrayerCategory, PrayerResponse, PrayerWall, PrayerTeam
from .serializers import (
    PrayerRequestSerializer, PrayerCategorySerializer, PrayerResponseSerializer,
    PrayerWallSerializer, PrayerTeamSerializer
)


class PrayerRequestPermission(permissions.BasePermission):
    """Custom permission for prayer requests"""

    def has_permission(self, request, view):
        if request.method == 'POST':  # Anyone can submit prayer requests
            return True
        # Only staff can view/manage prayer requests
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_ministry_lead)


class PrayerCategoryViewSet(viewsets.ModelViewSet):
    """API ViewSet for prayer categories"""
    queryset = PrayerCategory.objects.all()
    serializer_class = PrayerCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering = ['order', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Public users only see public categories
        if not (self.request.user.is_authenticated and 
               (self.request.user.is_admin or self.request.user.is_ministry_lead)):
            queryset = queryset.filter(is_public=True)
        return queryset


class PrayerRequestViewSet(viewsets.ModelViewSet):
    """API ViewSet for prayer requests"""
    queryset = PrayerRequest.objects.all()
    serializer_class = PrayerRequestSerializer
    permission_classes = [PrayerRequestPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['subject', 'message']
    filterset_fields = ['status', 'category', 'urgent', 'privacy_level', 'assigned_to']
    ordering_fields = ['submitted_at', 'updated_at']
    ordering = ['-submitted_at']

    def get_queryset(self):
        # Only staff can see prayer requests (except for creating)
        if self.action == 'create':
            return self.queryset

        if not (self.request.user.is_authenticated and 
               (self.request.user.is_admin or self.request.user.is_ministry_lead)):
            return PrayerRequest.objects.none()

        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def assign_to_me(self, request, pk=None):
        """Assign prayer request to current user"""
        prayer_request = self.get_object()
        prayer_request.assigned_to = request.user
        prayer_request.save()

        return Response({
            'success': True,
            'message': 'Prayer request assigned to you'
        })

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update prayer request status"""
        prayer_request = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(PrayerRequest.STATUS_CHOICES):
            return Response({
                'error': 'Invalid status'
            }, status=status.HTTP_400_BAD_REQUEST)

        prayer_request.status = new_status

        if new_status == 'reviewing':
            prayer_request.reviewed_at = timezone.now()
        elif new_status == 'answered':
            prayer_request.answered_at = timezone.now()

        prayer_request.save()

        return Response({
            'success': True,
            'message': f'Status updated to {prayer_request.get_status_display()}'
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get prayer request statistics"""
        total = PrayerRequest.objects.count()
        by_status = PrayerRequest.objects.values('status').annotate(count=Count('status'))
        urgent_count = PrayerRequest.objects.filter(urgent=True).count()

        return Response({
            'total_requests': total,
            'by_status': list(by_status),
            'urgent_requests': urgent_count,
        })


class PrayerResponseViewSet(viewsets.ModelViewSet):
    """API ViewSet for prayer responses"""
    queryset = PrayerResponse.objects.all()
    serializer_class = PrayerResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['prayer_request', 'is_public', 'is_internal']
    ordering = ['-created_at']

    def get_queryset(self):
        # Only staff can manage responses
        if not (self.request.user.is_admin or self.request.user.is_ministry_lead):
            return PrayerResponse.objects.none()
        return super().get_queryset()


class PrayerWallViewSet(viewsets.ModelViewSet):
    """API ViewSet for prayer wall posts"""
    queryset = PrayerWall.objects.all()
    serializer_class = PrayerWallSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    filterset_fields = ['is_approved', 'is_featured']
    ordering = ['-approved_at', '-submitted_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Public users only see approved posts
        if not (self.request.user.is_authenticated and 
               (self.request.user.is_admin or self.request.user.is_ministry_lead)):
            queryset = queryset.filter(is_approved=True)

        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a prayer wall post"""
        if not (request.user.is_admin or request.user.is_ministry_lead):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        post = self.get_object()
        post.is_approved = True
        post.approved_by = request.user
        post.approved_at = timezone.now()
        post.save()

        return Response({
            'success': True,
            'message': 'Prayer wall post approved'
        })

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured prayer wall posts"""
        featured_posts = self.get_queryset().filter(is_featured=True, is_approved=True)[:5]
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)


class PrayerTeamViewSet(viewsets.ModelViewSet):
    """API ViewSet for prayer team management"""
    queryset = PrayerTeam.objects.filter(is_active=True)
    serializer_class = PrayerTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['user__first_name', 'user__last_name']

    def get_queryset(self):
        # Only admins can manage prayer team
        if not self.request.user.is_admin:
            return PrayerTeam.objects.none()
        return super().get_queryset()
