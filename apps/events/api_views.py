from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from .models import Event, EventCategory, EventRegistration, EventAttendance
from .serializers import (
    EventSerializer, EventListSerializer, EventCategorySerializer,
    EventRegistrationSerializer
)


class IsOrganizerOrAdminOrReadOnly(permissions.BasePermission):
    """Permission for event management"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admins can edit everything
        if request.user.is_admin:
            return True

        # Organizers can edit their events
        if hasattr(obj, 'organizer') and obj.organizer == request.user:
            return True
        if hasattr(obj, 'co_organizers') and request.user in obj.co_organizers.all():
            return True

        return False


class EventCategoryViewSet(viewsets.ModelViewSet):
    """API ViewSet for event categories"""
    queryset = EventCategory.objects.filter(is_active=True)
    serializer_class = EventCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering = ['order', 'name']


class EventViewSet(viewsets.ModelViewSet):
    """API ViewSet for events"""
    queryset = Event.objects.all()
    permission_classes = [IsOrganizerOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location_name']
    filterset_fields = ['category', 'status', 'is_featured', 'requires_rsvp', 'is_virtual']
    ordering_fields = ['start_datetime', 'created_at', 'title']
    ordering = ['start_datetime']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Public users only see published events
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            queryset = queryset.filter(status='published')

        # Filter by time
        time_filter = self.request.query_params.get('time')
        now = timezone.now()

        if time_filter == 'upcoming':
            queryset = queryset.filter(start_datetime__gte=now)
        elif time_filter == 'past':
            queryset = queryset.filter(end_datetime__lt=now)
        elif time_filter == 'ongoing':
            queryset = queryset.filter(start_datetime__lte=now, end_datetime__gte=now)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        """Register for an event"""
        event = self.get_object()

        if not event.requires_rsvp:
            return Response({
                'error': 'This event does not require registration'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not event.is_registration_open:
            return Response({
                'error': 'Registration is not open for this event'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if already registered
        if event.registrations.filter(user=request.user).exists():
            return Response({
                'error': 'You are already registered for this event'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create registration
        registration_data = request.data.copy()
        registration_data['event'] = event.id

        serializer = EventRegistrationSerializer(data=registration_data, context={'request': request})
        if serializer.is_valid():
            registration = serializer.save()
            registration.status = 'confirmed'
            registration.payment_amount = event.registration_fee
            registration.save()

            return Response({
                'success': True,
                'message': f'Successfully registered for {event.title}',
                'registration': EventRegistrationSerializer(registration).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        """Cancel event registration"""
        event = self.get_object()

        try:
            registration = event.registrations.get(user=request.user)
            registration.status = 'cancelled'
            registration.save()

            return Response({
                'success': True,
                'message': f'Registration for {event.title} cancelled'
            })
        except EventRegistration.DoesNotExist:
            return Response({
                'error': 'You are not registered for this event'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        """Get event registrations (organizers and admins only)"""
        event = self.get_object()

        if not (request.user == event.organizer or request.user.is_admin or 
                request.user in event.co_organizers.all()):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        registrations = event.registrations.filter(status='confirmed')
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """API ViewSet for event registrations"""
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['event', 'status', 'payment_status']
    ordering = ['-registered_at']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Users can only see their own registrations unless admin/organizer
        if not user.is_admin:
            queryset = queryset.filter(
                Q(user=user) | 
                Q(event__organizer=user) | 
                Q(event__co_organizers=user)
            ).distinct()

        return queryset


class EventAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for event attendance (read-only)"""
    queryset = EventAttendance.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_admin:
            # Only see attendance for events user organizes
            return self.queryset.filter(
                Q(event__organizer=user) | Q(event__co_organizers=user)
            ).distinct()
        return super().get_queryset()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def calendar_events(request):
    """API endpoint for calendar view of events"""

    year = request.query_params.get('year')
    month = request.query_params.get('month')

    queryset = Event.objects.filter(status='published')

    if year and month:
        try:
            year = int(year)
            month = int(month)
            queryset = queryset.filter(start_datetime__year=year, start_datetime__month=month)
        except ValueError:
            pass

    events = queryset.order_by('start_datetime')
    serializer = EventListSerializer(events, many=True, context={'request': request})

    return Response(serializer.data)
