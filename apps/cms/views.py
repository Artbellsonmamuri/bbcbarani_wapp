from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import ContentSection, WelcomeScreen, ServiceSchedule, HeaderFooter, SEOSettings
from .forms import ContentSectionForm, WelcomeScreenForm, ServiceScheduleForm


def home(request):
    """Homepage view with welcome screen content"""
    try:
        welcome_content = ContentSection.objects.filter(
            section_type='welcome_screen', 
            status='published'
        ).first()
        welcome_screen = welcome_content.welcomescreen if welcome_content else None
    except:
        welcome_screen = None

    # Get recent blog posts for homepage
    recent_posts = ContentSection.objects.filter(
        section_type='blog_post',
        status='published'
    ).order_by('-publish_date')[:3]

    # Get service schedule
    services = ServiceSchedule.objects.filter(is_active=True).order_by('order')

    context = {
        'welcome_screen': welcome_screen,
        'recent_posts': recent_posts,
        'services': services,
    }
    return render(request, 'cms/home.html', context)


def section_detail(request, section_type):
    """Generic view for content sections"""
    content = get_object_or_404(
        ContentSection, 
        section_type=section_type, 
        status='published',
        language=request.LANGUAGE_CODE
    )

    # Handle specific section types
    template_name = f'cms/{section_type}.html'

    context = {
        'content': content,
        'section_type': section_type,
    }

    # Add specific context for different section types
    if section_type == 'schedule':
        context['services'] = ServiceSchedule.objects.filter(is_active=True).order_by('order')

    return render(request, template_name, context)


def contact_view(request):
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Store contact submission (could send email too)
        # TODO: Create ContactSubmission model or send email

        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('cms:contact')

    contact_content = ContentSection.objects.filter(
        section_type='contact',
        status='published'
    ).first()

    context = {
        'content': contact_content,
    }
    return render(request, 'cms/contact.html', context)


class ContentSectionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view to list content sections"""
    model = ContentSection
    template_name = 'cms/admin/content_list.html'
    context_object_name = 'sections'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_admin

    def get_queryset(self):
        queryset = ContentSection.objects.all()
        section_type = self.request.GET.get('type')
        status = self.request.GET.get('status')

        if section_type:
            queryset = queryset.filter(section_type=section_type)
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-updated_at')


class ContentSectionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Admin view to create content sections"""
    model = ContentSection
    form_class = ContentSectionForm
    template_name = 'cms/admin/content_form.html'
    success_url = reverse_lazy('cms:admin_content_list')

    def test_func(self):
        return self.request.user.is_admin

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, f'Content section "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class ContentSectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Admin view to update content sections"""
    model = ContentSection
    form_class = ContentSectionForm
    template_name = 'cms/admin/content_form.html'
    success_url = reverse_lazy('cms:admin_content_list')

    def test_func(self):
        return self.request.user.is_admin

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.version += 1
        messages.success(self.request, f'Content section "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


@staff_member_required
def admin_dashboard(request):
    """CMS admin dashboard"""
    # Get statistics
    total_sections = ContentSection.objects.count()
    published_sections = ContentSection.objects.filter(status='published').count()
    draft_sections = ContentSection.objects.filter(status='draft').count()

    # Recent content
    recent_content = ContentSection.objects.order_by('-updated_at')[:5]

    context = {
        'total_sections': total_sections,
        'published_sections': published_sections,
        'draft_sections': draft_sections,
        'recent_content': recent_content,
    }
    return render(request, 'cms/admin/dashboard.html', context)


@staff_member_required
def bulk_content_actions(request):
    """Handle bulk actions on content"""
    if request.method == 'POST':
        action = request.POST.get('action')
        content_ids = request.POST.getlist('content_ids')

        if action == 'publish':
            ContentSection.objects.filter(id__in=content_ids).update(status='published')
            messages.success(request, f'{len(content_ids)} sections published.')
        elif action == 'archive':
            ContentSection.objects.filter(id__in=content_ids).update(status='archived')
            messages.success(request, f'{len(content_ids)} sections archived.')
        elif action == 'delete':
            ContentSection.objects.filter(id__in=content_ids).delete()
            messages.success(request, f'{len(content_ids)} sections deleted.')

    return redirect('cms:admin_content_list')
