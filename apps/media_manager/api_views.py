from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import Media, MediaCategory
from .serializers import MediaSerializer, MediaCategorySerializer, MediaSearchSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission for media management"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class MediaViewSet(viewsets.ModelViewSet):
    """API ViewSet for media files"""
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'tags']
    filterset_fields = ['media_type', 'category', 'is_public']
    ordering_fields = ['created_at', 'title', 'file_size']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # If not admin, only show public media
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            queryset = queryset.filter(is_public=True)

        return queryset

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Handle bulk file uploads"""
        files = request.FILES.getlist('files')
        uploaded_media = []
        errors = []

        for file in files:
            try:
                media = Media.objects.create(
                    title=file.name.split('.')[0].replace('_', ' ').title(),
                    file=file,
                    uploaded_by=request.user,
                )
                uploaded_media.append(MediaSerializer(media).data)
            except Exception as e:
                errors.append(f"Failed to upload {file.name}: {str(e)}")

        return Response({
            'uploaded': uploaded_media,
            'errors': errors,
            'success': len(errors) == 0
        })

    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """Get usage information for a media file"""
        media = self.get_object()
        usage_instances = media.usage_instances.all()

        usage_data = []
        for usage in usage_instances:
            usage_data.append({
                'content_type': usage.content_type,
                'object_id': usage.object_id,
                'field_name': usage.field_name,
                'created_at': usage.created_at
            })

        return Response({
            'usage_count': media.usage_count,
            'usage_instances': usage_data
        })

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for media files"""
        serializer = MediaSearchSerializer(data=request.data)
        if serializer.is_valid():
            queryset = self.get_queryset()

            search_term = serializer.validated_data.get('search')
            category = serializer.validated_data.get('category')
            media_type = serializer.validated_data.get('media_type')
            tags = serializer.validated_data.get('tags')

            if search_term:
                queryset = queryset.filter(
                    Q(title__icontains=search_term) |
                    Q(description__icontains=search_term)
                )

            if category:
                queryset = queryset.filter(category_id=category)

            if media_type:
                queryset = queryset.filter(media_type=media_type)

            if tags:
                queryset = queryset.filter(tags__icontains=tags)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = MediaSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = MediaSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MediaCategoryViewSet(viewsets.ModelViewSet):
    """API ViewSet for media categories"""
    queryset = MediaCategory.objects.all()
    serializer_class = MediaCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def media_files(self, request, pk=None):
        """Get all media files in this category"""
        category = self.get_object()
        media_files = Media.objects.filter(category=category)
        serializer = MediaSerializer(media_files, many=True, context={'request': request})
        return Response(serializer.data)
