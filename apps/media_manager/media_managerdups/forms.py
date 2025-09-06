from django import forms
from django.core.validators import FileExtensionValidator
from .models import MediaFile, MediaFolder, MediaCollection


class MediaFileForm(forms.ModelForm):
    """Form for uploading and editing media files"""

    class Meta:
        model = MediaFile
        fields = [
            'title', 'description', 'file', 'folder', 'tags',
            'alt_text', 'caption', 'is_public', 'is_featured',
            'copyright_info', 'license_type'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Enter tags separated by commas',
                'help_text': 'Tags help organize and search your media files'
            }),
            'alt_text': forms.TextInput(attrs={
                'placeholder': 'Describe this image for accessibility'
            }),
            'caption': forms.Textarea(attrs={'rows': 2}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.txt'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter folders based on user permissions
        if self.user and not self.user.is_staff:
            from django.db.models import Q
            self.fields['folder'].queryset = MediaFolder.objects.filter(
                Q(is_public=True) | 
                Q(created_by=self.user) | 
                Q(allowed_users=self.user)
            ).distinct()

        # Add CSS classes
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ == 'CheckboxInput':
                field.widget.attrs['class'] = 'form-check-input'
            elif field.widget.__class__.__name__ in ['Select', 'SelectMultiple']:
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB.")

            # Check file extension
            allowed_extensions = [
                'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',  # Images
                'mp4', 'avi', 'mov', 'wmv', 'webm',  # Videos
                'mp3', 'wav', 'ogg', 'flac',  # Audio
                'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
                'zip', 'rar', '7z'  # Archives
            ]

            extension = file.name.split('.')[-1].lower()
            if extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"File type '{extension}' is not allowed. "
                    f"Allowed types: {', '.join(allowed_extensions)}"
                )

        return file

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if tags:
            # Clean and validate tags
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if len(tag_list) > 20:
                raise forms.ValidationError("Maximum 20 tags allowed.")

            # Check tag length
            for tag in tag_list:
                if len(tag) > 50:
                    raise forms.ValidationError("Tag length cannot exceed 50 characters.")

            return ', '.join(tag_list)
        return tags
