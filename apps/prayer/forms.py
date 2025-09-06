from django import forms
from django.core.exceptions import ValidationError
from .models import PrayerRequest, PrayerResponse, PrayerWall, PrayerCategory


class PrayerRequestForm(forms.ModelForm):
    """Public form for submitting prayer requests"""

    class Meta:
        model = PrayerRequest
        fields = [
            'requester_name', 'email', 'phone', 'category', 'subject', 
            'message', 'privacy_level', 'share_with_prayer_team', 
            'share_updates_via_email', 'urgent'
        ]
        widgets = {
            'requester_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email (optional, for updates)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (optional)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your prayer request'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Please share your prayer request with us...'
            }),
            'privacy_level': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = PrayerCategory.objects.filter(is_public=True).order_by('order')
        self.fields['category'].empty_label = "Select a category (optional)"

        # Help texts
        self.fields['privacy_level'].help_text = "Choose how you'd like your request to be handled"
        self.fields['urgent'].help_text = "Check if this is an urgent prayer need"

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 10:
            raise ValidationError("Please provide more details in your prayer request (at least 10 characters).")
        return message.strip()

    def clean(self):
        cleaned_data = super().clean()
        share_updates = cleaned_data.get('share_updates_via_email')
        email = cleaned_data.get('email')

        if share_updates and not email:
            raise ValidationError("Email is required if you want to receive updates.")

        return cleaned_data


class PrayerResponseForm(forms.ModelForm):
    """Form for staff to respond to prayer requests"""

    class Meta:
        model = PrayerResponse
        fields = ['message', 'is_public', 'is_internal', 'shared_with_prayer_team']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your response or update...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_public'].help_text = "Share this response with the person who submitted the request"
        self.fields['is_internal'].help_text = "This is an internal staff note"
        self.fields['shared_with_prayer_team'].help_text = "Share with the prayer team"


class PrayerWallForm(forms.ModelForm):
    """Form for submitting testimonies to the prayer wall"""

    class Meta:
        model = PrayerWall
        fields = ['title', 'content', 'author_name', 'related_prayer_request']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title of your testimony'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share how God answered your prayer or blessed you...'
            }),
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            # Limit related prayer requests to user's own requests
            self.fields['related_prayer_request'].queryset = PrayerRequest.objects.filter(
                Q(user=user) | Q(email=user.email)
            ).order_by('-submitted_at')
            self.fields['related_prayer_request'].empty_label = "Select related prayer request (optional)"
        else:
            self.fields['related_prayer_request'].widget = forms.HiddenInput()

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 20:
            raise ValidationError("Please share more details about your testimony (at least 20 characters).")
        return content.strip()


class QuickPrayerForm(forms.Form):
    """Simple prayer request form for homepage"""

    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name (optional)'
        })
    )
    prayer_request = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please pray for...'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email for updates (optional)'
        })
    )
