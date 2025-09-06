from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import PrayerRequest, PrayerCategory, PrayerResponse, PrayerWall
from .forms import PrayerRequestForm, PrayerResponseForm, PrayerWallForm


def submit_prayer_request(request):
    """Public view for submitting prayer requests"""

    if request.method == 'POST':
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer_request = form.save(commit=False)

            # If user is logged in, associate with user
            if request.user.is_authenticated:
                prayer_request.user = request.user

            prayer_request.save()

            # Send notification to staff (if configured)
            try:
                send_mail(
                    subject=f'New Prayer Request: {prayer_request.subject}',
                    message=f'A new prayer request has been submitted.\n\nFrom: {prayer_request.get_requester_name()}\n\nSubject: {prayer_request.subject}\n\nMessage: {prayer_request.message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except:
                pass

            messages.success(request, 
                'Thank you for your prayer request. Our prayer team will lift you up in prayer.')
            return redirect('prayer:submit')
    else:
        form = PrayerRequestForm()

    # Get recent prayer wall posts for encouragement
    recent_testimonies = PrayerWall.objects.filter(
        is_approved=True
    ).order_by('-approved_at')[:3]

    context = {
        'form': form,
        'categories': PrayerCategory.objects.filter(is_public=True).order_by('order'),
        'recent_testimonies': recent_testimonies,
    }
    return render(request, 'prayer/submit.html', context)


def prayer_wall(request):
    """Public prayer wall showing answered prayers and testimonies"""

    posts = PrayerWall.objects.filter(is_approved=True).order_by('-approved_at')
    featured_posts = posts.filter(is_featured=True)[:3]

    context = {
        'posts': posts,
        'featured_posts': featured_posts,
    }
    return render(request, 'prayer/wall.html', context)


def submit_testimony(request):
    """Allow users to submit prayer testimonies"""

    if request.method == 'POST':
        form = PrayerWallForm(request.POST)
        if form.is_valid():
            testimony = form.save(commit=False)

            if request.user.is_authenticated:
                testimony.author = request.user

            testimony.save()

            messages.success(request, 
                'Thank you for sharing your testimony! It will be reviewed before being posted.')
            return redirect('prayer:wall')
    else:
        form = PrayerWallForm()

    return render(request, 'prayer/submit_testimony.html', {'form': form})


# Admin Views
@staff_member_required
def prayer_admin_dashboard(request):
    """Dashboard for prayer request management"""

    # Statistics
    total_requests = PrayerRequest.objects.count()
    new_requests = PrayerRequest.objects.filter(status='new').count()
    urgent_requests = PrayerRequest.objects.filter(urgent=True, status__in=['new', 'reviewing']).count()

    # Recent requests
    recent_requests = PrayerRequest.objects.order_by('-submitted_at')[:10]

    # Requests by status
    status_counts = PrayerRequest.objects.values('status').annotate(count=Count('status'))

    context = {
        'total_requests': total_requests,
        'new_requests': new_requests,
        'urgent_requests': urgent_requests,
        'recent_requests': recent_requests,
        'status_counts': status_counts,
    }
    return render(request, 'prayer/admin/dashboard.html', context)


class PrayerRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view for listing prayer requests"""
    model = PrayerRequest
    template_name = 'prayer/admin/request_list.html'
    context_object_name = 'prayer_requests'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_ministry_lead

    def get_queryset(self):
        queryset = PrayerRequest.objects.all()

        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by assignment
        assigned = self.request.GET.get('assigned')
        if assigned == 'me':
            queryset = queryset.filter(assigned_to=self.request.user)
        elif assigned == 'unassigned':
            queryset = queryset.filter(assigned_to__isnull=True)

        # Filter urgent
        if self.request.GET.get('urgent') == 'true':
            queryset = queryset.filter(urgent=True)

        return queryset.order_by('-submitted_at')


@staff_member_required
def prayer_request_detail(request, request_id):
    """Detailed view for managing individual prayer requests"""

    prayer_request = get_object_or_404(PrayerRequest, id=request_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(PrayerRequest.STATUS_CHOICES):
                prayer_request.status = new_status

                if new_status == 'reviewing':
                    prayer_request.reviewed_at = timezone.now()
                elif new_status == 'answered':
                    prayer_request.answered_at = timezone.now()

                prayer_request.save()
                messages.success(request, f'Prayer request status updated to {prayer_request.get_status_display()}.')

        elif action == 'assign':
            prayer_request.assigned_to = request.user
            prayer_request.save()
            messages.success(request, 'Prayer request assigned to you.')

        elif action == 'add_response':
            response_form = PrayerResponseForm(request.POST)
            if response_form.is_valid():
                response = response_form.save(commit=False)
                response.prayer_request = prayer_request
                response.responder = request.user
                response.save()
                messages.success(request, 'Response added successfully.')
                return redirect('prayer:admin_detail', request_id=prayer_request.id)

        return redirect('prayer:admin_detail', request_id=prayer_request.id)

    response_form = PrayerResponseForm()

    context = {
        'prayer_request': prayer_request,
        'responses': prayer_request.responses.all().order_by('-created_at'),
        'response_form': response_form,
        'status_choices': PrayerRequest.STATUS_CHOICES,
    }
    return render(request, 'prayer/admin/request_detail.html', context)
