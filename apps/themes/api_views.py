from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SiteTheme, ColorPalette, FontFamily, ThemeCustomization
from .serializers import (
    SiteThemeSerializer, ColorPaletteSerializer, FontFamilySerializer,
    ThemeCustomizationSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission for theme management"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class SiteThemeViewSet(viewsets.ModelViewSet):
    """API ViewSet for site themes"""
    queryset = SiteTheme.objects.all()
    serializer_class = SiteThemeSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering = ['name']

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a theme"""
        theme = self.get_object()
        theme.activate()

        return Response({
            'success': True,
            'message': f'Theme "{theme.name}" activated',
            'compiled_css': theme.get_compiled_css()
        })

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a theme"""
        original = self.get_object()

        new_theme = SiteTheme.objects.create(
            name=f"{original.name} (Copy)",
            description=f"Copy of {original.description}",
            css_settings=original.css_settings.copy(),
            custom_css=original.custom_css,
            created_by=request.user
        )

        serializer = self.get_serializer(new_theme)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active theme"""
        active_theme = SiteTheme.objects.filter(is_active=True).first()
        if active_theme:
            serializer = self.get_serializer(active_theme)
            return Response(serializer.data)
        return Response({'error': 'No active theme'}, status=status.HTTP_404_NOT_FOUND)


class ColorPaletteViewSet(viewsets.ModelViewSet):
    """API ViewSet for color palettes"""
    queryset = ColorPalette.objects.filter(is_active=True)
    serializer_class = ColorPaletteSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering = ['name']


class FontFamilyViewSet(viewsets.ModelViewSet):
    """API ViewSet for font families"""
    queryset = FontFamily.objects.filter(is_active=True)
    serializer_class = FontFamilySerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering = ['category', 'name']


class ThemeCustomizationViewSet(viewsets.ModelViewSet):
    """API ViewSet for user theme customizations"""
    queryset = ThemeCustomization.objects.all()
    serializer_class = ThemeCustomizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own customizations
        return self.queryset.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_active_theme(request):
    """Get CSS for the currently active theme"""

    active_theme = SiteTheme.objects.filter(is_active=True).first()

    if active_theme:
        return Response({
            'theme_name': active_theme.name,
            'css_settings': active_theme.css_settings,
            'css_variables': active_theme.get_css_variables(),
            'compiled_css': active_theme.get_compiled_css(),
        })

    return Response({'error': 'No active theme found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def preview_theme(request, theme_id):
    """Preview a theme without activating it"""

    if not request.user.is_admin:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    theme = get_object_or_404(SiteTheme, id=theme_id)

    # Apply any preview settings from query params
    preview_settings = request.query_params.get('settings')
    if preview_settings:
        import json
        try:
            css_settings = json.loads(preview_settings)
            # Create temporary theme object
            preview_theme = SiteTheme(
                name=theme.name,
                css_settings=css_settings,
                custom_css=theme.custom_css
            )
        except json.JSONDecodeError:
            preview_theme = theme
    else:
        preview_theme = theme

    return Response({
        'theme_name': preview_theme.name,
        'css_settings': preview_theme.css_settings,
        'compiled_css': preview_theme.get_compiled_css(),
    })
