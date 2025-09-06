from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import Ministry, MinistryCategory, MinistryMember, MinistryEvent
from .serializers import (
    MinistrySerializer, MinistryListSerializer, MinistryCategorySerializer,
    MinistryMemberSerializer, MinistryEventSerializer
)


class IsAdminOrMinistryLead(permissions.BasePermission):
    """Permission for ministry management"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_ministry_lead)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admins can edit everything
        if request.user.is_admin:
            return True

        # Ministry leads can edit their own ministries
        if hasattr(obj, 'leader') and obj.leader == request.user:
            return True
        if hasattr(obj, 'co_leaders') and request.user in obj.co_leaders.all():
            return True

        return False


class MinistryCategoryViewSet(viewsets.ModelViewSet):
    """API ViewSet for ministry categories"""
    queryset = MinistryCategory.objects.all()
    serializer_class = MinistryCategorySerializer
    permission_classes = [IsAdminOrMinistryLead]
    ordering = ['order', 'name']


class MinistryViewSet(viewsets.ModelViewSet):
    """API ViewSet for ministries"""
    queryset = Ministry.objects.all()
    permission_classes = [IsAdminOrMinistryLead]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'short_description', 'full_description']
    filterset_fields = ['category', 'is_active', 'featured', 'requires_membership']
    ordering_fields = ['title', 'created_at', 'order']
    ordering = ['order', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return MinistryListSerializer
        return MinistrySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Public users only see active ministries
        if not (self.request.user.is_authenticated and 
               (self.request.user.is_admin or self.request.user.is_ministry_lead)):
            queryset = queryset.filter(is_active=True)

        # Ministry leads see only their ministries (unless admin)
        elif not self.request.user.is_admin:
            queryset = queryset.filter(
                Q(leader=self.request.user) | 
                Q(co_leaders=self.request.user)
            ).distinct()

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        """Allow authenticated users to join a ministry"""
        ministry = self.get_object()

        if ministry.requires_membership and not request.user.is_active_member:
            return Response({
                'error': 'This ministry requires church membership'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if already a member
        if MinistryMember.objects.filter(ministry=ministry, user=request.user).exists():
            return Response({
                'error': 'You are already a member of this ministry'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create membership
        membership = MinistryMember.objects.create(
            ministry=ministry,
            user=request.user,
            role='member'
        )

        return Response({
            'success': True,
            'message': f'Successfully joined {ministry.title}',
            'membership': MinistryMemberSerializer(membership).data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, pk=None):
        """Allow users to leave a ministry"""
        ministry = self.get_object()

        try:
            membership = MinistryMember.objects.get(ministry=ministry, user=request.user)
            membership.delete()

            return Response({
                'success': True,
                'message': f'Successfully left {ministry.title}'
            })
        except MinistryMember.DoesNotExist:
            return Response({
                'error': 'You are not a member of this ministry'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get ministry members"""
        ministry = self.get_object()
        members = ministry.ministry_members.filter(is_active=True).select_related('user')
        serializer = MinistryMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get ministry events"""
        ministry = self.get_object()
        events = ministry.ministry_events.filter(is_public=True).order_by('start_datetime')
        serializer = MinistryEventSerializer(events, many=True)
        return Response(serializer.data)


class MinistryMemberViewSet(viewsets.ModelViewSet):
    """API ViewSet for ministry members"""
    queryset = MinistryMember.objects.all()
    serializer_class = MinistryMemberSerializer
    permission_classes = [IsAdminOrMinistryLead]
    filterset_fields = ['ministry', 'role', 'is_active']
    ordering = ['ministry__title', 'user__first_name']


class MinistryEventViewSet(viewsets.ModelViewSet):
    """API ViewSet for ministry events"""
    queryset = MinistryEvent.objects.all()
    serializer_class = MinistryEventSerializer
    permission_classes = [IsAdminOrMinistryLead]
    filterset_fields = ['ministry', 'is_public', 'is_featured', 'requires_registration']
    ordering = ['start_datetime']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Public users only see public events
        if not (self.request.user.is_authenticated and 
               (self.request.user.is_admin or self.request.user.is_ministry_lead)):
            queryset = queryset.filter(is_public=True)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
