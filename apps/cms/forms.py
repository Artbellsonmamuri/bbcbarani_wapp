from django import forms
from django.core.exceptions import ValidationError
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import ContentSection, WelcomeScreen, ServiceSchedule, HeaderFooter


class ContentSectionForm(forms.ModelForm):
    """Form for editing content sections"""

    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = ContentSection
        fields = [
            'section_type', 'title', 'slug', 'body', 'excerpt',
            'meta_title', 'meta_description', 'meta_keywords', 'og_image',
            'status', 'featured', 'publish_date', 'language', 'order'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'structured_content': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meta_title'].help_text = "If blank, will use the main title"
        self.fields['meta_description'].help_text = "If blank, will use the excerpt"

    def clean_meta_title(self):
        meta_title = self.cleaned_data.get('meta_title')
        if meta_title and len(meta_title) > 70:
            raise ValidationError("Meta title should be 70 characters or less for better SEO.")
        return meta_title

    def clean_meta_description(self):
        meta_description = self.cleaned_data.get('meta_description')
        if meta_description and len(meta_description) > 160:
            raise ValidationError("Meta description should be 160 characters or less for better SEO.")
        return meta_description


class WelcomeScreenForm(forms.ModelForm):
    """Form for editing welcome screen content"""

    class Meta:
        model = WelcomeScreen
        fields = [
            'welcome_message', 'subtitle', 'pastor_name', 'pastor_title', 
            'pastor_photo', 'pastor_bio', 'church_logo', 'carousel_images',
            'cta_text', 'cta_link'
        ]
        widgets = {
            'welcome_message': forms.Textarea(attrs={'rows': 4}),
            'pastor_bio': forms.Textarea(attrs={'rows': 5}),
            'carousel_images': forms.CheckboxSelectMultiple,
        }


class ServiceScheduleForm(forms.ModelForm):
    """Form for editing service schedules"""

    class Meta:
        model = ServiceSchedule
        fields = [
            'service_name', 'day_of_week', 'start_time', 'end_time',
            'location_name', 'address', 'description', 'special_notes',
            'live_stream_enabled', 'live_stream_platform', 'live_stream_url',
            'is_active', 'order'
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'special_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and end_time <= start_time:
            raise ValidationError("End time must be after start time.")

        live_stream_enabled = cleaned_data.get('live_stream_enabled')
        live_stream_url = cleaned_data.get('live_stream_url')

        if live_stream_enabled and not live_stream_url:
            raise ValidationError("Live stream URL is required when live streaming is enabled.")

        return cleaned_data


class HeaderFooterForm(forms.ModelForm):
    """Form for editing header and footer content"""

    class Meta:
        model = HeaderFooter
        fields = [
            'section', 'content', 'show_language_switcher', 'show_search',
            'copyright_text', 'footer_message', 'phone', 'email', 'address',
            'facebook_url', 'youtube_url', 'instagram_url', 'twitter_url'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'json-editor'}),
            'footer_message': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ContactForm(forms.Form):
    """Public contact form"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 6, 
            'placeholder': 'Your Message'
        })
    )

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        return message
