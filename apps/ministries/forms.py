from django import forms
from django.core.exceptions import ValidationError
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Ministry, MinistryMember, MinistryEvent, MinistryCategory


class MinistryForm(forms.ModelForm):
    """Form for creating and editing ministries"""

    full_description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Ministry
        fields = [
            'title', 'slug', 'category', 'short_description', 'full_description',
            'icon_type', 'font_icon', 'custom_icon', 'carousel_images',
            'leader', 'co_leaders', 'contact_email', 'contact_phone',
            'meeting_location', 'meeting_schedule', 'is_active', 'featured',
            'allow_public_contact', 'requires_membership', 'order',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'meeting_schedule': forms.Textarea(attrs={'rows': 3}),
            'carousel_images': forms.CheckboxSelectMultiple,
            'co_leaders': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['font_icon'].help_text = "Font Awesome class (e.g., fas fa-cross, fas fa-heart)"
        self.fields['carousel_images'].queryset = self.fields['carousel_images'].queryset.filter(media_type='image')

    def clean(self):
        cleaned_data = super().clean()
        icon_type = cleaned_data.get('icon_type')
        font_icon = cleaned_data.get('font_icon')
        custom_icon = cleaned_data.get('custom_icon')

        if icon_type == 'font' and not font_icon:
            raise ValidationError("Font icon is required when icon type is 'font'.")
        elif icon_type == 'image' and not custom_icon:
            raise ValidationError("Custom icon image is required when icon type is 'image'.")

        return cleaned_data


class MinistryMemberForm(forms.ModelForm):
    """Form for managing ministry membership"""

    class Meta:
        model = MinistryMember
        fields = ['ministry', 'user', 'role', 'skills', 'availability', 'notes', 'is_active']
        widgets = {
            'skills': forms.TextInput(attrs={'placeholder': 'e.g., Music, Teaching, Organization'}),
            'availability': forms.TextInput(attrs={'placeholder': 'e.g., Weekends, Evenings'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class MinistryEventForm(forms.ModelForm):
    """Form for creating ministry events"""

    class Meta:
        model = MinistryEvent
        fields = [
            'ministry', 'title', 'description', 'start_datetime', 'end_datetime',
            'location', 'requires_registration', 'max_attendees', 'registration_deadline',
            'contact_person', 'contact_email', 'contact_phone', 'featured_image',
            'is_public', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        registration_deadline = cleaned_data.get('registration_deadline')

        if start_datetime and end_datetime and end_datetime <= start_datetime:
            raise ValidationError("End time must be after start time.")

        if registration_deadline and start_datetime and registration_deadline >= start_datetime:
            raise ValidationError("Registration deadline must be before the event start time.")

        requires_registration = cleaned_data.get('requires_registration')
        max_attendees = cleaned_data.get('max_attendees')

        if requires_registration and not max_attendees:
            raise ValidationError("Maximum attendees is required when registration is enabled.")

        return cleaned_data


class MinistryContactForm(forms.Form):
    """Public form for contacting ministry leadership"""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your Message'
        })
    )

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        return message


class MinistryJoinForm(forms.Form):
    """Form for users to express interest in joining a ministry"""

    INTEREST_LEVELS = [
        ('interested', 'Interested in Learning More'),
        ('volunteer', 'Want to Volunteer'),
        ('member', 'Want to Become a Member'),
        ('leadership', 'Interested in Leadership Role'),
    ]

    interest_level = forms.ChoiceField(
        choices=INTEREST_LEVELS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    skills = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'What skills or experience do you have?'
        })
    )
    availability = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'When are you available?'
        })
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional message or questions'
        })
    )
