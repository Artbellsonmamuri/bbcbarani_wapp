from django import forms
from django.core.exceptions import ValidationError
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import BlogPost, Comment, BlogSubscriber, BlogCategory


class BlogPostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""

    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'excerpt', 'content', 'featured_image', 'category', 'tags',
            'status', 'published_date', 'featured', 'sticky', 'allow_comments',
            'comments_require_approval', 'meta_title', 'meta_description', 'meta_keywords', 'og_image'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'published_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Comma-separated tags'}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter images for featured_image and og_image
        from apps.media_manager.models import Media
        image_queryset = Media.objects.filter(media_type='image')
        self.fields['featured_image'].queryset = image_queryset
        self.fields['og_image'].queryset = image_queryset

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


class CommentForm(forms.ModelForm):
    """Form for submitting comments on blog posts"""

    class Meta:
        model = Comment
        fields = ['content', 'guest_name', 'guest_email', 'guest_website', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts...'
            }),
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email (will not be published)'
            }),
            'guest_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your website (optional)'
            }),
            'parent': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If user is authenticated, hide guest fields
        if user and user.is_authenticated:
            self.fields['guest_name'].widget = forms.HiddenInput()
            self.fields['guest_email'].widget = forms.HiddenInput()
            self.fields['guest_website'].widget = forms.HiddenInput()

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        return content.strip()


class SubscribeForm(forms.ModelForm):
    """Form for subscribing to blog updates"""

    class Meta:
        model = BlogSubscriber
        fields = ['email', 'name', 'categories', 'frequency']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional)'
            }),
            'categories': forms.CheckboxSelectMultiple,
            'frequency': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = BlogCategory.objects.filter(is_active=True).order_by('order')
        self.fields['categories'].required = False
        self.fields['categories'].help_text = "Select categories you're interested in (leave blank for all)"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BlogSubscriber.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("This email is already subscribed.")
        return email


class CommentReplyForm(forms.ModelForm):
    """Form for replying to comments"""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your reply...'
            }),
        }


class BlogSearchForm(forms.Form):
    """Form for searching blog posts"""

    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search blog posts...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=BlogCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    author = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        empty_label="All Authors",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get authors who have published posts
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['author'].queryset = User.objects.filter(
            blog_posts__status='published'
        ).distinct().order_by('first_name', 'last_name')
