from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class SiteTheme(models.Model):
    """Site theme configurations with CSS settings"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # CSS Settings stored as JSON
    css_settings = models.JSONField(default=dict, help_text="Theme configuration as JSON")

    # Custom CSS override
    custom_css = models.TextField(blank=True, help_text="Additional custom CSS")

    # Theme preview
    preview_image = models.ImageField(upload_to='theme_previews/', blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=False, help_text="Currently active theme")
    is_default = models.BooleanField(default=False, help_text="Default theme for new users")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_themes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Site Theme')
        verbose_name_plural = _('Site Themes')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}" + (" (Active)" if self.is_active else "")

    def save(self, *args, **kwargs):
        # Ensure only one theme is active at a time
        if self.is_active:
            SiteTheme.objects.filter(is_active=True).update(is_active=False)

        # Ensure only one default theme
        if self.is_default:
            SiteTheme.objects.filter(is_default=True).update(is_default=False)

        super().save(*args, **kwargs)

    def activate(self):
        """Activate this theme"""
        SiteTheme.objects.filter(is_active=True).update(is_active=False)
        self.is_active = True
        self.save()

    def get_css_variables(self):
        """Convert CSS settings to CSS custom properties"""
        if not self.css_settings:
            return ""

        css_vars = []
        for key, value in self.css_settings.items():
            css_key = key.replace('_', '-')
            css_vars.append(f"--{css_key}: {value};")

        return "\n".join(css_vars)

    def get_compiled_css(self):
        """Get the complete CSS for this theme"""
        css_variables = self.get_css_variables()

        compiled_css = f"""
        :root {{
            {css_variables}
        }}

        {self.custom_css}
        """

        return compiled_css


class ThemeCustomization(models.Model):
    """User-specific theme customizations"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='theme_customization')
    theme = models.ForeignKey(SiteTheme, on_delete=models.CASCADE)

    # Custom overrides
    custom_settings = models.JSONField(default=dict)
    custom_css = models.TextField(blank=True)

    # Settings
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Theme Customization')
        verbose_name_plural = _('Theme Customizations')

    def __str__(self):
        return f"{self.user.username} - {self.theme.name}"


class ColorPalette(models.Model):
    """Predefined color palettes for themes"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Color definitions
    primary_color = models.CharField(max_length=7, help_text="Primary brand color")
    secondary_color = models.CharField(max_length=7, help_text="Secondary color")
    accent_color = models.CharField(max_length=7, help_text="Accent color")

    # Text colors
    text_color = models.CharField(max_length=7, default="#333333")
    text_light = models.CharField(max_length=7, default="#666666")
    text_muted = models.CharField(max_length=7, default="#999999")

    # Background colors
    background_color = models.CharField(max_length=7, default="#ffffff")
    background_alt = models.CharField(max_length=7, default="#f8f9fa")

    # Status colors
    success_color = models.CharField(max_length=7, default="#28a745")
    warning_color = models.CharField(max_length=7, default="#ffc107")
    danger_color = models.CharField(max_length=7, default="#dc3545")
    info_color = models.CharField(max_length=7, default="#17a2b8")

    # Settings
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Color Palette')
        verbose_name_plural = _('Color Palettes')
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_css_variables(self):
        """Convert color palette to CSS custom properties"""
        return {
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'accent_color': self.accent_color,
            'text_color': self.text_color,
            'text_light': self.text_light,
            'text_muted': self.text_muted,
            'background_color': self.background_color,
            'background_alt': self.background_alt,
            'success_color': self.success_color,
            'warning_color': self.warning_color,
            'danger_color': self.danger_color,
            'info_color': self.info_color,
        }


class FontFamily(models.Model):
    """Available font families for themes"""

    name = models.CharField(max_length=100, unique=True)
    font_family = models.CharField(max_length=255, help_text="CSS font-family value")
    google_fonts_url = models.URLField(blank=True, help_text="Google Fonts import URL")

    # Categories
    category = models.CharField(max_length=50, choices=[
        ('serif', 'Serif'),
        ('sans-serif', 'Sans Serif'),
        ('monospace', 'Monospace'),
        ('display', 'Display'),
        ('handwriting', 'Handwriting'),
    ], default='sans-serif')

    # Preview
    preview_text = models.CharField(max_length=255, default="The quick brown fox jumps over the lazy dog")

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Font Family')
        verbose_name_plural = _('Font Families')
        ordering = ['category', 'name']

    def __str__(self):
        return self.name
