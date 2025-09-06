from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, Comment, BlogSubscriber
from .forms import BlogPostForm, CommentForm, SubscribeForm


class BlogListView(ListView):
    """Public blog listing view"""
    model = BlogPost
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).select_related('author', 'category', 'featured_image')

        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )

        # Order: sticky posts first, then by date
        return queryset.order_by('-sticky', '-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Categories for sidebar
        context['categories'] = BlogCategory.objects.filter(is_active=True).annotate(
            post_count=Count('blogpost', filter=Q(blogpost__status='published'))
        ).filter(post_count__gt=0)

        # Featured posts for sidebar
        context['featured_posts'] = BlogPost.objects.filter(
            status='published',
            featured=True
        ).exclude(id__in=[post.id for post in context['posts']]).order_by('-published_date')[:5]

        # Recent posts for sidebar
        context['recent_posts'] = BlogPost.objects.filter(
            status='published'
        ).exclude(id__in=[post.id for post in context['posts']]).order_by('-published_date')[:5]

        return context


class BlogDetailView(DetailView):
    """Detailed view for individual blog posts"""
    model = BlogPost
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('co_authors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Track view
        self.track_view()

        # Get approved comments
        comments = post.comments.filter(status='approved', parent__isnull=True).order_by('created_at')
        context['comments'] = comments
        context['comment_count'] = post.comment_count

        # Comment form
        context['comment_form'] = CommentForm()

        # Related posts
        context['related_posts'] = BlogPost.objects.filter(
            status='published',
            category=post.category
        ).exclude(pk=post.pk).order_by('-published_date')[:3]

        return context

    def track_view(self):
        """Track page view for analytics"""
        from .models import BlogPostView

        # Get client IP
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        # Create view record
        BlogPostView.objects.create(
            blog_post=self.get_object(),
            ip_address=ip,
            user=self.request.user if self.request.user.is_authenticated else None,
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            referer=self.request.META.get('HTTP_REFERER', '')
        )

        # Update view count
        BlogPost.objects.filter(pk=self.get_object().pk).update(view_count=models.F('view_count') + 1)


def add_comment(request, post_slug):
    """Handle comment submission"""
    post = get_object_or_404(BlogPost, slug=post_slug, status='published', allow_comments=True)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog_post = post

            if request.user.is_authenticated:
                comment.user = request.user

            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                comment.ip_address = x_forwarded_for.split(',')[0]
            else:
                comment.ip_address = request.META.get('REMOTE_ADDR')

            comment.user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Set status based on post settings
            if post.comments_require_approval:
                comment.status = 'pending'
                messages.info(request, 'Your comment has been submitted and is awaiting approval.')
            else:
                comment.status = 'approved'
                messages.success(request, 'Your comment has been posted!')

            comment.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Comment submitted successfully!',
                    'requires_approval': post.comments_require_approval
                })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})

    return redirect('blog:detail', slug=post_slug)


def subscribe_to_blog(request):
    """Handle blog subscription"""
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscriber = form.save()

            # TODO: Send verification email

            messages.success(request, 'Thank you for subscribing! Please check your email to confirm.')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})

    return redirect('blog:list')


# Admin Views
@staff_member_required
def blog_admin_dashboard(request):
    """Blog admin dashboard"""

    # Statistics
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(status='published').count()
    draft_posts = BlogPost.objects.filter(status='draft').count()
    pending_comments = Comment.objects.filter(status='pending').count()

    # Recent activity
    recent_posts = BlogPost.objects.order_by('-updated_at')[:5]
    recent_comments = Comment.objects.order_by('-created_at')[:10]

    # Popular posts (by views)
    popular_posts = BlogPost.objects.filter(status='published').order_by('-view_count')[:5]

    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'pending_comments': pending_comments,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'popular_posts': popular_posts,
    }
    return render(request, 'blog/admin/dashboard.html', context)


@staff_member_required
def moderate_comments(request):
    """Comment moderation interface"""

    comments = Comment.objects.filter(status='pending').order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        comment_ids = request.POST.getlist('comment_ids')

        if action == 'approve':
            Comment.objects.filter(id__in=comment_ids).update(
                status='approved',
                moderated_by=request.user,
                moderated_at=timezone.now()
            )
            messages.success(request, f'{len(comment_ids)} comments approved.')
        elif action == 'reject':
            Comment.objects.filter(id__in=comment_ids).update(
                status='rejected',
                moderated_by=request.user,
                moderated_at=timezone.now()
            )
            messages.success(request, f'{len(comment_ids)} comments rejected.')
        elif action == 'spam':
            Comment.objects.filter(id__in=comment_ids).update(
                status='spam',
                moderated_by=request.user,
                moderated_at=timezone.now()
            )
            messages.success(request, f'{len(comment_ids)} comments marked as spam.')

    context = {
        'comments': comments,
    }
    return render(request, 'blog/admin/moderate_comments.html', context)
