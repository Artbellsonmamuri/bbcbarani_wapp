from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Media, MediaCategory
from .forms import MediaUploadForm, MediaCategoryForm
import json


class MediaLibraryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view for media library"""
    model = Media
    template_name = 'media_manager/library.html'
    context_object_name = 'media_files'
    paginate_by = 24

    def test_func(self):
        return self.request.user.is_admin

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by media type
        media_type = self.request.GET.get('type')
        if media_type:
            queryset = queryset.filter(media_type=media_type)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(tags__icontains=search)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = MediaCategory.objects.all()
        context['media_types'] = Media.MEDIA_TYPES
        return context


@login_required
def media_upload(request):
    """Handle media file uploads"""
    if not request.user.is_admin:
        return HttpResponseForbidden("You don't have permission to upload media.")

    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.uploaded_by = request.user
            media.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX response
                return JsonResponse({
                    'success': True,
                    'media': {
                        'id': media.id,
                        'title': media.title,
                        'url': media.file.url,
                        'thumbnail': media.get_thumbnail_url(),
                        'type': media.media_type,
                    }
                })
            else:
                messages.success(request, f'Media file "{media.title}" uploaded successfully!')
                return redirect('media_manager:library')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = MediaUploadForm()

    return render(request, 'media_manager/upload.html', {'form': form})


@login_required
def media_detail(request, media_id):
    """View and edit media details"""
    if not request.user.is_admin:
        return HttpResponseForbidden("You don't have permission to view media details.")

    media = get_object_or_404(Media, id=media_id)

    if request.method == 'POST':
        form = MediaUploadForm(request.POST, instance=media)
        if form.is_valid():
            form.save()
            messages.success(request, f'Media "{media.title}" updated successfully!')
            return redirect('media_manager:detail', media_id=media.id)
    else:
        form = MediaUploadForm(instance=media)

    context = {
        'media': media,
        'form': form,
        'usage_instances': media.usage_instances.all()[:10],
    }
    return render(request, 'media_manager/detail.html', context)


@login_required
def media_delete(request, media_id):
    """Delete media file"""
    if not request.user.is_admin:
        return HttpResponseForbidden("You don't have permission to delete media.")

    media = get_object_or_404(Media, id=media_id)

    if request.method == 'POST':
        # Check if media is being used
        if media.usage_instances.exists():
            messages.warning(request, f'Cannot delete "{media.title}" - it is currently being used.')
            return redirect('media_manager:detail', media_id=media.id)

        # Delete file from storage
        if media.file:
            default_storage.delete(media.file.name)

        media.delete()
        messages.success(request, f'Media file "{media.title}" deleted successfully!')
        return redirect('media_manager:library')

    return render(request, 'media_manager/delete_confirm.html', {'media': media})


@method_decorator(csrf_exempt, name='dispatch')
class MediaBulkUploadView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Handle bulk media uploads"""

    def test_func(self):
        return self.request.user.is_admin

    def post(self, request):
        files = request.FILES.getlist('files')
        uploaded_media = []
        errors = []

        for file in files:
            try:
                media = Media.objects.create(
                    title=file.name,
                    file=file,
                    uploaded_by=request.user,
                )
                uploaded_media.append({
                    'id': media.id,
                    'title': media.title,
                    'url': media.file.url,
                    'type': media.media_type,
                })
            except Exception as e:
                errors.append(f"Failed to upload {file.name}: {str(e)}")

        return JsonResponse({
            'success': len(errors) == 0,
            'uploaded': uploaded_media,
            'errors': errors,
        })
