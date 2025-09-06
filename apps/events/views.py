from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.utils import timezone
from .models import Event, EventCategory, EventRegistration, EventAttendance
from .forms import EventForm, EventRegistrationForm


class EventListView(ListView):
    """Public event listing view"""
    model = Event
    template_name = 'events/list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        queryset = Event.objects.filter(status='published').select_related('category', 'organizer')

        # Filter by time period
        time_filter = self.request.GET.get('time', 'upcoming')
        now = timezone.now()

        if time_filter == 'upcoming':
            queryset = queryset.filter(start_datetime__gte=now)
        elif time_filter == 'past':
            queryset = queryset.filter(end_datetime__lt=now)
        elif time_filter == 'ongoing':
            queryset = queryset.filter(start_datetime__lte=now, end_datetime__gte=now)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location_name__icontains=search)
            )

        return queryset.order_by('start_datetime' if time_filter != 'past' else '-start_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Categories with event counts
        context['categories'] = EventCategory.objects.filter(is_active=True).annotate(
            event_count=Count('event', filter=Q(event__status='published'))
        ).filter(event_count__gt=0)

        # Featured events
        context['featured_events'] = Event.objects.filter(
            status='published',
            is_featured=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:3]

        # Time filter options
        context['time_filter'] = self.request.GET.get('time', 'upcoming')

        return context


class EventDetailView(DetailView):
    """Detailed view for individual events"""
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Event.objects.filter(status='published').select_related('category', 'organizer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()

        # Registration form if RSVP is required
        if event.requires_rsvp:
            context['registration_form'] = EventRegistrationForm()
            context['user_registration'] = None

            # Check if user is already registered
            if self.request.user.is_authenticated:
                try:
                    context['user_registration'] = EventRegistration.objects.get(
                        event=event,
                        user=self.request.user
                    )
                except EventRegistration.DoesNotExist:
                    pass

        # Related events
        context['related_events'] = Event.objects.filter(
            status='published',
            category=event.category,
            start_datetime__gte=timezone.now()
        ).exclude(pk=event.pk).order_by('start_datetime')[:3]

        return context


@login_required
def register_for_event(request, event_slug):
    """Handle event registration"""
    event = get_object_or_404(Event, slug=event_slug, status='published', requires_rsvp=True)

    # Check if registration is open
    if not event.is_registration_open:
        messages.error(request, 'Registration for this event is no longer available.')
        return redirect('events:detail', slug=event_slug)

    # Check if user is already registered
    if event.registrations.filter(user=request.user).exists():
        messages.info(request, 'You are already registered for this event.')
        return redirect('events:detail', slug=event_slug)

    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.user = request.user
            registration.status = 'confirmed'

            # Calculate payment
            registration.payment_amount = event.registration_fee

            registration.save()

            messages.success(request, f'Successfully registered for {event.title}!')
            return redirect('events:detail', slug=event_slug)
    else:
        form = EventRegistrationForm()

    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'events/register.html', context)


@login_required
def cancel_registration(request, event_slug):
    """Allow users to cancel their event registration"""
    event = get_object_or_404(Event, slug=event_slug)

    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)

        if request.method == 'POST':
            registration.status = 'cancelled'
            registration.save()

            messages.success(request, f'Your registration for {event.title} has been cancelled.')
            return redirect('events:detail', slug=event_slug)

        return render(request, 'events/cancel_registration.html', {
            'event': event,
            'registration': registration
        })
    except EventRegistration.DoesNotExist:
        messages.error(request, 'You are not registered for this event.')
        return redirect('events:detail', slug=event_slug)


def event_calendar(request):
    """Calendar view of events"""
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)

    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month

    # Get events for the month
    events = Event.objects.filter(
        status='published',
        start_datetime__year=year,
        start_datetime__month=month
    ).order_by('start_datetime')

    context = {
        'events': events,
        'year': year,
        'month': month,
        'current_date': timezone.now(),
    }
    return render(request, 'events/calendar.html', context)


# Admin Views
@staff_member_required
def events_admin_dashboard(request):
    """Events admin dashboard"""

    now = timezone.now()

    # Statistics
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(start_datetime__gte=now, status='published').count()
    ongoing_events = Event.objects.filter(
        start_datetime__lte=now, 
        end_datetime__gte=now,
        status='published'
    ).count()

    # Registration statistics
    total_registrations = EventRegistration.objects.filter(status='confirmed').count()

    # Recent activity
    recent_events = Event.objects.order_by('-created_at')[:5]
    recent_registrations = EventRegistration.objects.order_by('-registered_at')[:10]

    context = {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'ongoing_events': ongoing_events,
        'total_registrations': total_registrations,
        'recent_events': recent_events,
        'recent_registrations': recent_registrations,
    }
    return render(request, 'events/admin/dashboard.html', context)


@staff_member_required
def event_check_in(request, event_id):
    """Check-in interface for events"""
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        registration_id = request.POST.get('registration_id')
        if registration_id:
            try:
                registration = EventRegistration.objects.get(id=registration_id, event=event)
                registration.checked_in_at = timezone.now()
                registration.checked_in_by = request.user
                registration.status = 'attended'
                registration.save()

                # Create attendance record
                EventAttendance.objects.create(
                    event=event,
                    registration=registration,
                    checked_in_by=request.user
                )

                messages.success(request, f'{registration.get_registrant_name()} checked in successfully!')
            except EventRegistration.DoesNotExist:
                messages.error(request, 'Registration not found.')

        # Handle walk-in attendees
        walk_in_name = request.POST.get('walk_in_name')
        walk_in_email = request.POST.get('walk_in_email')

        if walk_in_name:
            EventAttendance.objects.create(
                event=event,
                walk_in_name=walk_in_name,
                walk_in_email=walk_in_email,
                checked_in_by=request.user
            )
            messages.success(request, f'{walk_in_name} checked in as walk-in.')

    registrations = event.registrations.filter(status='confirmed').order_by('guest_name', 'user__first_name')
    attendance_records = event.attendance_records.all().order_by('-checked_in_at')

    context = {
        'event': event,
        'registrations': registrations,
        'attendance_records': attendance_records,
        'checked_in_count': attendance_records.count(),
    }
    return render(request, 'events/admin/check_in.html', context)
