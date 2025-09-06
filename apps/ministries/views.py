from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from .models import Ministry, MinistryCategory, MinistryMember, MinistryEvent
from .forms import MinistryForm, MinistryMemberForm, MinistryEventForm


class MinistryListView(ListView):
    """Public view listing all active ministries"""
    model = Ministry
    template_name = 'ministries/list.html'
    context_object_name = 'ministries'
    paginate_by = 12

    def get_queryset(self):
        queryset = Ministry.objects.filter(is_active=True)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(full_description__icontains=search)
            )

        return queryset.order_by('order', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = MinistryCategory.objects.annotate(
            ministry_count=Count('ministry')
        ).filter(ministry_count__gt=0)
        context['featured_ministries'] = Ministry.objects.filter(
            is_active=True, featured=True
        ).order_by('order')[:6]
        return context


class MinistryDetailView(DetailView):
    """Public detail view for a ministry"""
    model = Ministry
    template_name = 'ministries/detail.html'
    context_object_name = 'ministry'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Ministry.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ministry = self.get_object()

        # Get active members
        context['members'] = ministry.ministry_members.filter(is_active=True).select_related('user')

        # Get upcoming events
        from django.utils import timezone
        context['upcoming_events'] = ministry.ministry_events.filter(
            is_public=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:5]

        # Get other ministries in the same category
        if ministry.category:
            context['related_ministries'] = Ministry.objects.filter(
                category=ministry.category,
                is_active=True
            ).exclude(pk=ministry.pk).order_by('order')[:3]

        return context


@login_required
def join_ministry(request, ministry_id):
    """Allow users to join a ministry"""
    ministry = get_object_or_404(Ministry, id=ministry_id, is_active=True)

    if ministry.requires_membership and not request.user.is_active_member:
        messages.warning(request, "This ministry requires church membership.")
        return redirect('ministries:detail', slug=ministry.slug)

    # Check if already a member
    if MinistryMember.objects.filter(ministry=ministry, user=request.user).exists():
        messages.info(request, f"You are already a member of {ministry.title}.")
        return redirect('ministries:detail', slug=ministry.slug)

    if request.method == 'POST':
        # Create membership
        MinistryMember.objects.create(
            ministry=ministry,
            user=request.user,
            role='member'
        )

        messages.success(request, f"You have successfully joined {ministry.title}!")

        # TODO: Send notification to ministry leader

        return redirect('ministries:detail', slug=ministry.slug)

    return render(request, 'ministries/join_confirm.html', {'ministry': ministry})


@login_required
def leave_ministry(request, ministry_id):
    """Allow users to leave a ministry"""
    ministry = get_object_or_404(Ministry, id=ministry_id)

    try:
        membership = MinistryMember.objects.get(ministry=ministry, user=request.user)

        if request.method == 'POST':
            membership.delete()
            messages.success(request, f"You have left {ministry.title}.")
            return redirect('ministries:detail', slug=ministry.slug)

        return render(request, 'ministries/leave_confirm.html', {
            'ministry': ministry,
            'membership': membership
        })
    except MinistryMember.DoesNotExist:
        messages.error(request, "You are not a member of this ministry.")
        return redirect('ministries:detail', slug=ministry.slug)


# Admin Views
class MinistryAdminListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view for managing ministries"""
    model = Ministry
    template_name = 'ministries/admin/list.html'
    context_object_name = 'ministries'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_ministry_lead

    def get_queryset(self):
        queryset = Ministry.objects.all()

        # Ministry leads can only see their own ministries
        if not self.request.user.is_admin:
            queryset = queryset.filter(
                Q(leader=self.request.user) | 
                Q(co_leaders=self.request.user)
            ).distinct()

        return queryset.order_by('-updated_at')


def ministry_contact(request, ministry_id):
    """Handle ministry contact form"""
    ministry = get_object_or_404(Ministry, id=ministry_id, is_active=True, allow_public_contact=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # TODO: Send email to ministry leader
        # TODO: Create notification

        messages.success(request, f"Your message has been sent to {ministry.title} leadership!")
        return redirect('ministries:detail', slug=ministry.slug)

    return render(request, 'ministries/contact.html', {'ministry': ministry})


def ministries_by_category(request, category_slug):
    """List ministries by category"""
    category = get_object_or_404(MinistryCategory, slug=category_slug)
    ministries = Ministry.objects.filter(category=category, is_active=True).order_by('order')

    context = {
        'category': category,
        'ministries': ministries,
    }
    return render(request, 'ministries/category.html', context)
