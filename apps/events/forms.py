from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Event, EventRegistration, EventCategory


class EventForm(forms.ModelForm):
    """Form for creating and editing events"""

    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Event
        fields = [
            'title', 'slug', 'short_description', 'description', 'featured_image',
            'category', 'start_datetime', 'end_datetime', 'timezone',
            'location_name', 'address', 'is_virtual', 'virtual_link',
            'requires_rsvp', 'max_attendees', 'registration_deadline',
            'allow_guest_registration', 'registration_fee',
            'contact_person', 'contact_email', 'contact_phone',
            'status', 'is_featured', 'meta_title', 'meta_description'
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'registration_fee': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        registration_deadline = cleaned_data.get('registration_deadline')
        requires_rsvp = cleaned_data.get('requires_rsvp')
        max_attendees = cleaned_data.get('max_attendees')

        # Validate datetime sequence
        if start_datetime and end_datetime and end_datetime <= start_datetime:
            raise ValidationError("End time must be after start time.")

        if registration_deadline and start_datetime and registration_deadline >= start_datetime:
            raise ValidationError("Registration deadline must be before event start time.")

        # Validate RSVP settings
        if requires_rsvp and not max_attendees:
            cleaned_data['max_attendees'] = 999999  # Default to very high number

        # Virtual event validation
        is_virtual = cleaned_data.get('is_virtual')
        virtual_link = cleaned_data.get('virtual_link')
        if is_virtual and not virtual_link:
            raise ValidationError("Virtual link is required for virtual events.")

        return cleaned_data


class EventRegistrationForm(forms.ModelForm):
    """Form for event registration/RSVP"""

    class Meta:
        model = EventRegistration
        fields = [
            'guest_name', 'guest_email', 'guest_phone', 'number_of_attendees',
            'attendee_names', 'dietary_restrictions', 'special_requirements',
            'registration_notes'
        ]
        widgets = {
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email'
            }),
            'guest_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (optional)'
            }),
            'number_of_attendees': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'attendee_names': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Names of additional attendees (if any)'
            }),
            'dietary_restrictions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any dietary restrictions or allergies?'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special requirements or accessibility needs?'
            }),
            'registration_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes or comments'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

        # If user is authenticated, prefill and hide guest fields
        if user and user.is_authenticated:
            self.fields['guest_name'].initial = user.get_full_name()
            self.fields['guest_email'].initial = user.email
            self.fields['guest_name'].widget = forms.HiddenInput()
            self.fields['guest_email'].widget = forms.HiddenInput()

        # Adjust max attendees based on event capacity
        if event and event.max_attendees:
            remaining_spots = event.spots_available
            if remaining_spots:
                self.fields['number_of_attendees'].widget.attrs['max'] = remaining_spots

    def clean_number_of_attendees(self):
        number = self.cleaned_data.get('number_of_attendees')
        if number < 1:
            raise ValidationError("Number of attendees must be at least 1.")
        return number


class EventSearchForm(forms.Form):
    """Form for searching and filtering events"""

    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=EventCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    time_filter = forms.ChoiceField(
        choices=[
            ('upcoming', 'Upcoming'),
            ('past', 'Past'),
            ('ongoing', 'Ongoing'),
            ('all', 'All'),
        ],
        initial='upcoming',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
