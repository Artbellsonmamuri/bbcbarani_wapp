from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.utils.text import slugify
import json
import mimetypes
from .models import MediaFile, MediaFolder, MediaCollection, MediaDownload
from .forms import MediaFileForm, MediaFolderForm, MediaCollectionForm


class MediaLibraryView(LoginRequiredMixin, ListView):
    """Main media library view"""
    model = MediaFile
    template_name = 'media_manager/library.html'
    context_object_name = 'media_files'
    paginate_by = 24

    def get_queryset(self):
        queryset = MediaFile.objects.all()

        # Filter by user permissions
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_public=True) | Q(uploaded_by=self.request.user)
            )

        # Filter by folder
        folder_slug = self.request.GET.get('folder')
        if folder_slug:
            try:
                folder = MediaFolder.objects.get(slug=folder_slug)
                if folder.can_access(self.request.user):
                    queryset = queryset.filter(folder=folder)
                else:
                    messages.error(self.request, "You don't have access to this folder.")
            except MediaFolder.DoesNotExist:
                messages.error(self.request, "Folder not found.")

        # Filter by media type
        media_type = self.request.GET.get('type')
        if media_type:
            queryset = queryset.filter(media_type=media_type)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search) |
                Q(original_filename__icontains=search)
            )

        # Sort
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get folders accessible to user
        folders = MediaFolder.objects.all()
        if not self.request.user.is_staff:
            folders = folders.filter(
                Q(is_public=True) | Q(created_by=self.request.user) | Q(allowed_users=self.request.user)
            ).distinct()

        # Media type counts
        media_counts = MediaFile.objects.values('media_type').annotate(count=Count('id'))

        context.update({
            'folders': folders,
            'media_counts': {item['media_type']: item['count'] for item in media_counts},
            'current_folder': self.request.GET.get('folder'),
            'current_type': self.request.GET.get('type'),
            'current_search': self.request.GET.get('search'),
            'current_sort': self.request.GET.get('sort', '-created_at'),
        })
        return context


class MediaDetailView(LoginRequiredMixin, DetailView):
    """Media file detail view"""
    model = MediaFile
    template_name = 'media_manager/detail.html'
    context_object_name = 'media_file'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.can_access(self.request.user):
            raise Http404("Media file not found or access denied.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get usage records
        usage_records = self.object.usage_records.filter(is_active=True)

        # Get related media (same tags or folder)
        related_media = MediaFile.objects.filter(
            Q(folder=self.object.folder) | Q(tags__overlap=self.object.get_tags_list())
        ).exclude(id=self.object.id)

        if not self.request.user.is_staff:
            related_media = related_media.filter(
                Q(is_public=True) | Q(uploaded_by=self.request.user)
            )

        related_media = related_media.distinct()[:6]

        context.update({
            'usage_records': usage_records,
            'related_media': related_media,
            'can_edit': self.object.can_edit(self.request.user),
        })
        return context


@login_required
def media_download(request, pk):
    """Download media file and track download"""
    media_file = get_object_or_404(MediaFile, pk=pk)

    if not media_file.can_access(request.user):
        raise Http404("Media file not found or access denied.")

    # Track download
    MediaDownload.objects.create(
        media_file=media_file,
        downloaded_by=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referer=request.META.get('HTTP_REFERER', '')
    )

    # Increment usage counter
    media_file.increment_usage()

    # Serve file
    response = HttpResponse(media_file.file.read(), content_type=media_file.mime_type)
    response['Content-Disposition'] = f'attachment; filename="{media_file.original_filename}"'
    return response


@login_required
@require_http_methods(["POST"])
def ajax_upload(request):
    """AJAX file upload endpoint"""

    if not request.FILES.get('file'):
        return JsonResponse({'error': 'No file provided'}, status=400)

    file_obj = request.FILES['file']

    # Basic validation
    if file_obj.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        return JsonResponse({'error': 'File too large'}, status=400)

    # Create media file
    mime_type, _ = mimetypes.guess_type(file_obj.name)

    media_file = MediaFile.objects.create(
        file=file_obj,
        original_filename=file_obj.name,
        file_size=file_obj.size,
        mime_type=mime_type or 'application/octet-stream',
        uploaded_by=request.user,
        folder_id=request.POST.get('folder_id') or None
    )

    return JsonResponse({
        'success': True,
        'media_file': {
            'id': media_file.id,
            'title': media_file.title,
            'url': media_file.file.url,
            'thumbnail_url': media_file.thumbnail_url,
            'media_type': media_file.media_type,
            'file_size': media_file.formatted_file_size,
        }
    })


@staff_member_required
def media_dashboard(request):
    """Admin dashboard for media management"""

    # Statistics
    total_files = MediaFile.objects.count()
    total_size = MediaFile.objects.aggregate(
        Sum('file_size')
    )['file_size__sum'] or 0

    # Media type breakdown
    media_stats = MediaFile.objects.values('media_type').annotate(
        count=Count('id'),
        size=Sum('file_size')
    ).order_by('-count')

    # Recent uploads
    recent_uploads = MediaFile.objects.order_by('-created_at')[:10]

    # Most used files
    popular_files = MediaFile.objects.order_by('-usage_count')[:10]

    # Storage usage by month
    from django.db.models import TruncMonth
    monthly_uploads = MediaFile.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id'),
        size=Sum('file_size')
    ).order_by('-month')[:12]

    context = {
        'total_files': total_files,
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'media_stats': media_stats,
        'recent_uploads': recent_uploads,
        'popular_files': popular_files,
        'monthly_uploads': list(monthly_uploads),
    }
    return render(request, 'media_manager/admin/dashboard.html', context)
