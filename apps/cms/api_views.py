from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ContentSection, WelcomeScreen, ServiceSchedule, HeaderFooter, SEOSettings
from .serializers import (
    ContentSectionSerializer, WelcomeScreenSerializer, ServiceScheduleSerializer,
    HeaderFooterSerializer, SEOSettingsSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow admins to edit content."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class ContentSectionViewSet(viewsets.ModelViewSet):
    """API ViewSet for content sections"""
    queryset = ContentSection.objects.all()
    serializer_class = ContentSectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['section_type', 'status', 'language', 'featured']
    search_fields = ['title', 'body', 'meta_title']
    ordering_fields = ['created_at', 'updated_at', 'order']
    ordering = ['-updated_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # If not admin, only show published content
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            queryset = queryset.filter(status='published')

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def revert_to_revision(self, request, pk=None):
        """Revert content to a specific revision"""
        content = self.get_object()
        revision_number = request.data.get('revision_number')

        if not request.user.is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            revision = content.revisions.get(revision_number=revision_number)
            content.title = revision.title
            content.body = revision.body
            content.structured_content = revision.structured_content
            content.updated_by = request.user
            content.version += 1
            content.save()

            return Response({'success': True, 'message': f'Reverted to revision {revision_number}'})
        except:
            return Response({'error': 'Revision not found'}, status=status.HTTP_404_NOT_FOUND)


class WelcomeScreenViewSet(viewsets.ModelViewSet):
    """API ViewSet for welcome screens"""
    queryset = WelcomeScreen.objects.all()
    serializer_class = WelcomeScreenSerializer
    permission_classes = [IsAdminOrReadOnly]


class ServiceScheduleViewSet(viewsets.ModelViewSet):
    """API ViewSet for service schedules"""
    queryset = ServiceSchedule.objects.filter(is_active=True)
    serializer_class = ServiceScheduleSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering = ['order', 'day_of_week', 'start_time']


class HeaderFooterAPIView(APIView):
    """API View for header and footer content"""
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        header = HeaderFooter.objects.filter(section='header').first()
        footer = HeaderFooter.objects.filter(section='footer').first()

        return Response({
            'header': HeaderFooterSerializer(header).data if header else None,
            'footer': HeaderFooterSerializer(footer).data if footer else None,
        })

    def post(self, request):
        section = request.data.get('section')
        if section not in ['header', 'footer']:
            return Response({'error': 'Invalid section'}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = HeaderFooter.objects.get_or_create(section=section)
        serializer = HeaderFooterSerializer(obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SEOSettingsAPIView(APIView):
    """API View for SEO settings"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        settings = SEOSettings.objects.first()
        if settings:
            return Response(SEOSettingsSerializer(settings).data)
        return Response({})

    def post(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        settings, created = SEOSettings.objects.get_or_create(defaults=request.data)
        if not created:
            serializer = SEOSettingsSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(SEOSettingsSerializer(settings).data, status=status.HTTP_201_CREATED)
