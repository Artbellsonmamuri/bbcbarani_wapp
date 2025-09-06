from django import forms
from django.core.exceptions import ValidationError
import json
from .models import SiteTheme, ColorPalette, FontFamily, ThemeCustomization


class SiteThemeForm(forms.ModelForm):
    """Form for creating and editing site themes"""

    class Meta:
        model = SiteTheme
        fields = ['name', 'description', 'css_settings', 'custom_css', 'preview_image', 'is_active', 'is_default']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'css_settings': forms.Textarea(attrs={
                'rows': 10,
                'class': 'code-editor',
                'placeholder': '{"primary_color": "#007bff", "font_family": "Arial, sans-serif"}'
            }),
            'custom_css': forms.Textarea(attrs={
                'rows': 15,
                'class': 'code-editor',
                'placeholder': '/* Custom CSS rules */'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['css_settings'].help_text = "JSON object with CSS variable definitions"

    def clean_css_settings(self):
        css_settings = self.cleaned_data.get('css_settings')
        if css_settings:
            try:
                if isinstance(css_settings, str):
                    json.loads(css_settings)
                elif isinstance(css_settings, dict):
                    json.dumps(css_settings)
            except (json.JSONDecodeError, TypeError):
                raise ValidationError("CSS settings must be valid JSON.")
        return css_settings


class ColorPaletteForm(forms.ModelForm):
    """Form for creating color palettes"""

    class Meta:
        model = ColorPalette
        fields = [
            'name', 'description', 'primary_color', 'secondary_color', 'accent_color',
            'text_color', 'text_light', 'text_muted', 'background_color', 'background_alt',
            'success_color', 'warning_color', 'danger_color', 'info_color', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color'}),
            'text_color': forms.TextInput(attrs={'type': 'color'}),
            'text_light': forms.TextInput(attrs={'type': 'color'}),
            'text_muted': forms.TextInput(attrs={'type': 'color'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'background_alt': forms.TextInput(attrs={'type': 'color'}),
            'success_color': forms.TextInput(attrs={'type': 'color'}),
            'warning_color': forms.TextInput(attrs={'type': 'color'}),
            'danger_color': forms.TextInput(attrs={'type': 'color'}),
            'info_color': forms.TextInput(attrs={'type': 'color'}),
        }


class ThemeCustomizationForm(forms.ModelForm):
    """Form for user theme customizations"""

    class Meta:
        model = ThemeCustomization
        fields = ['theme', 'custom_settings', 'custom_css', 'is_active']
        widgets = {
            'custom_settings': forms.Textarea(attrs={
                'rows': 8,
                'class': 'code-editor',
                'placeholder': '{"primary_color": "#custom-color"}'
            }),
            'custom_css': forms.Textarea(attrs={
                'rows': 10,
                'class': 'code-editor',
                'placeholder': '/* Your custom CSS */'
            }),
        }


class ThemeBuilderForm(forms.Form):
    """Visual form for building themes using color pickers"""

    theme_name = forms.CharField(max_length=100)
    base_theme = forms.ModelChoiceField(
        queryset=SiteTheme.objects.all(),
        required=False,
        empty_label="Start from scratch"
    )
    color_palette = forms.ModelChoiceField(
        queryset=ColorPalette.objects.filter(is_active=True),
        required=False,
        empty_label="Choose color palette"
    )

    # Color settings
    primary_color = forms.CharField(
        max_length=7,
        widget=forms.TextInput(attrs={'type': 'color', 'value': '#007bff'})
    )
    secondary_color = forms.CharField(
        max_length=7,
        widget=forms.TextInput(attrs={'type': 'color', 'value': '#6c757d'})
    )
    background_color = forms.CharField(
        max_length=7,
        widget=forms.TextInput(attrs={'type': 'color', 'value': '#ffffff'})
    )

    # Typography
    heading_font = forms.ModelChoiceField(
        queryset=FontFamily.objects.filter(is_active=True),
        required=False
    )
    body_font = forms.ModelChoiceField(
        queryset=FontFamily.objects.filter(is_active=True),
        required=False
    )

    # Layout settings
    container_width = forms.ChoiceField(
        choices=[
            ('1200px', 'Standard (1200px)'),
            ('1400px', 'Wide (1400px)'),
            ('100%', 'Full Width'),
        ],
        initial='1200px'
    )
    border_radius = forms.ChoiceField(
        choices=[
            ('0px', 'Square (0px)'),
            ('4px', 'Slightly Rounded (4px)'),
            ('8px', 'Rounded (8px)'),
            ('16px', 'Very Rounded (16px)'),
        ],
        initial='8px'
    )
