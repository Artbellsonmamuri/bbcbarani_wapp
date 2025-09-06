from django import forms
from .models import NotificationPreference, AnnouncementBanner


class NotificationPreferenceForm(forms.ModelForm):
    """Form for user notification preferences"""

    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'email_frequency', 'in_app_enabled',
            'show_desktop_notifications', 'sms_enabled', 'phone_number',
            'blog_notifications', 'event_notifications', 'comment_notifications',
            'prayer_notifications', 'system_notifications', 'marketing_notifications',
            'quiet_hours_enabled', 'quiet_start_time', 'quiet_end_time'
        ]
        widgets = {
            'email_frequency': forms.Select(attrs={'class': 'form-select'}),
            'quiet_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'quiet_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add CSS classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'

        # Prayer notifications only for ministry leads and admins
        user = kwargs.get('instance', {}).get('user') if 'instance' in kwargs else None
        if user and not (user.is_staff or getattr(user, 'role', None) == 'ministry_lead'):
            self.fields['prayer_notifications'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        # Validate quiet hours
        quiet_enabled = cleaned_data.get('quiet_hours_enabled')
        quiet_start = cleaned_data.get('quiet_start_time')
        quiet_end = cleaned_data.get('quiet_end_time')

        if quiet_enabled:
            if not quiet_start or not quiet_end:
                raise forms.ValidationError(
                    "Start and end times are required when quiet hours are enabled."
                )

        # Validate phone number if SMS is enabled
        sms_enabled = cleaned_data.get('sms_enabled')
        phone_number = cleaned_data.get('phone_number')

        if sms_enabled and not phone_number:
            raise forms.ValidationError(
                "Phone number is required when SMS notifications are enabled."
            )

        return cleaned_data


class CustomNotificationForm(forms.Form):
    """Form for sending custom notifications"""

    RECIPIENT_CHOICES = [
        ('all', 'All Users'),
        ('admins', 'Administrators Only'),
        ('members', 'Members Only'),
        ('ministry_leads', 'Ministry Leaders'),
    ]

    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('announcement', 'Announcement'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Notification title'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Notification message'
        })
    )
    notification_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        initial='info',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        initial='normal',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    recipients = forms.ChoiceField(
        choices=RECIPIENT_CHOICES,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    send_email = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    action_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com (optional)'
        })
    )
    action_text = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Action button text (optional)'
        })
    )
