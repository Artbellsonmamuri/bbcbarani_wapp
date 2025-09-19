"""
Bible Baptist Church CMS - Views
Complete view system for content display
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import Homepage, Page, Post, Event, Ministry, HeroSlide

def home(request):
    """Homepage view with hero carousel and latest content"""
    homepage = Homepage.objects.filter(published=True).first()
    hero_slides = HeroSlide.objects.filter(published=True).order_by('order', 'created_at')
    featured_posts = Post.objects.filter(published=True, is_featured=True)[:3]
    upcoming_events = Event.objects.filter(
        published=True, 
        start_date__gte=timezone.now()
    ).order_by('start_date')[:3]
    
    context = {
        'homepage': homepage,
        'hero_slides': hero_slides,  # <- Add this for carousel
        'featured_posts': featured_posts,
        'upcoming_events': upcoming_events,
        'navigation_pages': Page.objects.filter(published=True, show_in_navigation=True).order_by('navigation_order')
    }
    return render(request, 'cms/home.html', context)


def page_detail(request, slug):
    """Individual page view"""
    page = get_object_or_404(Page, slug=slug, published=True)
    context = {
        'page': page,
        'navigation_pages': Page.objects.filter(published=True, show_in_navigation=True).order_by('navigation_order')
    }
    return render(request, 'cms/page_detail.html', context)

def post_list(request):
    """Blog/news listing"""
    posts = Post.objects.filter(published=True).order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    # Compute tag lists for each post on the current page
    for p in posts:
        p.tags_list = [t.strip() for t in (p.tags or "").split(",") if t.strip()]
    
    context = {
        'posts': posts,
        'search': search,
        'navigation_pages': Page.objects.filter(published=True, show_in_navigation=True).order_by('navigation_order')
    }
    return render(request, 'cms/post_list.html', context)

def post_detail(request, slug):
    """Individual blog post"""
    post = get_object_or_404(Post, slug=slug, published=True)
    related_posts = (
        Post.objects.filter(published=True)
        .exclude(id=post.id)
        .order_by('-created_at')[:3]
    )

    # Compute a clean list of tags from the comma-separated string field
    tags = [t.strip() for t in (post.tags or "").split(",") if t.strip()]

    context = {
        'post': post,
        'tags': tags,  # <- add this
        'related_posts': related_posts,
        'navigation_pages': Page.objects.filter(
            published=True, show_in_navigation=True
        ).order_by('navigation_order'),
    }
    return render(request, 'cms/post_detail.html', context)

def event_list(request):
    """Events listing"""
    # Separate upcoming and past events
    upcoming_events = Event.objects.filter(
        published=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    past_events = Event.objects.filter(
        published=True,
        start_date__lt=timezone.now()
    ).order_by('-start_date')
    
    # Pagination for past events
    paginator = Paginator(past_events, 10)
    page_number = request.GET.get('page')
    past_events = paginator.get_page(page_number)
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'navigation_pages': Page.objects.filter(published=True, show_in_navigation=True).order_by('navigation_order')
    }
    return render(request, 'cms/event_list.html', context)

def event_detail(request, slug):
    """Individual event"""
    event = get_object_or_404(Event, slug=slug, published=True)
    related_events = Event.objects.filter(
        published=True,
        start_date__gte=timezone.now()
    ).exclude(id=event.id).order_by('start_date')[:3]
    
    context = {
        'event': event,
        'related_events': related_events,
        'navigation_pages': Page.objects.filter(published=True, show_in_navigation=True).order_by('navigation_order')
    }
    return render(request, 'cms/event_detail.html', context)

def ministry_list(request):
    """Ministries listing"""
    ministries = Ministry.objects.filter(published=True, is_active=True).order_by('title')
    
    context = {
        'ministries': ministries,
        'navigation_pages': Page.objects.filter(published=True, show_in_navigation=True).order_by('navigation_order')
    }
    return render(request, 'cms/ministry_list.html', context)

def ministry_detail(request, slug):
    """Individual ministry"""
    ministry = get_object_or_404(Ministry, slug=slug, published=True, is_active=True)
    
    context = {
        'ministry': ministry,
        'navigation_pages': Page.objects.filter(published=True, show_in_navigation=True).order_by('navigation_order')
    }
    return render(request, 'cms/ministry_detail.html', context)
