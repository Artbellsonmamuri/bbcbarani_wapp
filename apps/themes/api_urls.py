from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'themes', api_views.SiteThemeViewSet)
router.register(r'color-palettes', api_views.ColorPaletteViewSet)
router.register(r'font-families', api_views.FontFamilyViewSet)
router.register(r'customizations', api_views.ThemeCustomizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('active/', api_views.get_active_theme, name='active'),
    path('preview/<int:theme_id>/', api_views.preview_theme, name='preview'),
]
