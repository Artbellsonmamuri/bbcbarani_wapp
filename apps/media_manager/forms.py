from django import forms
from django.core.validators import FileExtensionValidator
from .models import Media, MediaCategory


class MediaUploadForm(forms.ModelForm):
    """Form for uploading and editing media files"""

    class Meta:
        model = Media
        fields = ['title', 'description', 'file', 'alt_text', 'category', 'tags', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'file': forms.FileInput(attrs={'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Comma-separated tags'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})
        self.fields['alt_text'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['tags'].widget.attrs.update({'class': 'form-control'})

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (10MB max)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB.")

            # Validate file type
            allowed_extensions = [
                'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',  # Images
                'mp4', 'avi', 'mov', 'wmv', 'webm',          # Videos
                'mp3', 'wav', 'ogg', 'm4a',                  # Audio
                'pdf', 'doc', 'docx', 'txt'                  # Documents
            ]

            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"File type '.{file_extension}' is not allowed.")

        return file


class MediaCategoryForm(forms.ModelForm):
    """Form for creating and editing media categories"""

    class Meta:
        model = MediaCategory
        fields = ['name', 'description', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class MediaSearchForm(forms.Form):
    """Form for searching media files"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search media files...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=MediaCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    media_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Media.MEDIA_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
