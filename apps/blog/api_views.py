from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from .models import BlogPost, BlogCategory, Comment, BlogSubscriber
from .serializers import (
    BlogPostSerializer, BlogPostListSerializer, BlogCategorySerializer,
    CommentSerializer, BlogSubscriberSerializer
)


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Permission for blog post management"""

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

        # Authors can edit their own posts
        if hasattr(obj, 'author') and obj.author == request.user:
            return True

        return False


class BlogCategoryViewSet(viewsets.ModelViewSet):
    """API ViewSet for blog categories"""
    queryset = BlogCategory.objects.filter(is_active=True)
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering = ['order', 'name']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts in this category"""
        category = self.get_object()
        posts = BlogPost.objects.filter(
            category=category,
            status='published',
            published_date__lte=timezone.now()
        ).order_by('-published_date')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class BlogPostViewSet(viewsets.ModelViewSet):
    """API ViewSet for blog posts"""
    queryset = BlogPost.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content', 'tags']
    filterset_fields = ['category', 'author', 'status', 'featured']
    ordering_fields = ['published_date', 'created_at', 'view_count', 'title']
    ordering = ['-published_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        return BlogPostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Public users only see published posts
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            queryset = queryset.filter(
                status='published',
                published_date__lte=timezone.now()
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Track views when retrieving a post"""
        response = super().retrieve(request, *args, **kwargs)

        # Track view if it's a published post
        instance = self.get_object()
        if instance.status == 'published':
            from .models import BlogPostView

            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            BlogPostView.objects.create(
                blog_post=instance,
                ip_address=ip,
                user=request.user if request.user.is_authenticated else None,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referer=request.META.get('HTTP_REFERER', '')
            )

            # Update view count
            BlogPost.objects.filter(pk=instance.pk).update(view_count=models.F('view_count') + 1)

        return response

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured blog posts"""
        featured_posts = self.get_queryset().filter(featured=True)[:5]
        serializer = BlogPostListSerializer(featured_posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular blog posts by view count"""
        popular_posts = self.get_queryset().order_by('-view_count')[:10]
        serializer = BlogPostListSerializer(popular_posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related blog posts"""
        post = self.get_object()
        related_posts = BlogPost.objects.filter(
            status='published',
            category=post.category
        ).exclude(pk=post.pk).order_by('-published_date')[:5]

        serializer = BlogPostListSerializer(related_posts, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """API ViewSet for comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['blog_post', 'status', 'user']
    ordering = ['created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Public users only see approved comments
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            queryset = queryset.filter(status='approved')

        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a comment"""
        if not request.user.is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        comment.status = 'approved'
        comment.moderated_by = request.user
        comment.moderated_at = timezone.now()
        comment.save()

        return Response({'success': True, 'message': 'Comment approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a comment"""
        if not request.user.is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        comment.status = 'rejected'
        comment.moderated_by = request.user
        comment.moderated_at = timezone.now()
        comment.save()

        return Response({'success': True, 'message': 'Comment rejected'})


class BlogSubscriberViewSet(viewsets.ModelViewSet):
    """API ViewSet for blog subscribers"""
    queryset = BlogSubscriber.objects.all()
    serializer_class = BlogSubscriberSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Only admins can see subscriber list
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            return BlogSubscriber.objects.none()
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        """Public endpoint for subscribing"""
        # Anyone can subscribe
        return super().create(request, *args, **kwargs)
