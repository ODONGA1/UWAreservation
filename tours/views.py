# In tours/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Tour
from booking.models import Availability

def tour_list(request):
    """
    A view to show all tours with enhanced information.
    """
    tours = Tour.objects.select_related('park').prefetch_related('availability').all()
    
    # Add availability info to each tour
    for tour in tours:
        tour.next_available = tour.availability.filter(
            date__gte=timezone.now().date(),
            slots_available__gt=0
        ).first()
        tour.total_upcoming = tour.availability.filter(
            date__gte=timezone.now().date(),
            slots_available__gt=0
        ).count()
    
    context = {'tours': tours}
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, tour_id):
    """
    A view to show the details of a single tour.
    """
    tour = get_object_or_404(Tour.objects.select_related('park'), pk=tour_id)
    
    # Get upcoming availabilities
    upcoming_availabilities = Availability.objects.filter(
        tour=tour,
        date__gte=timezone.now().date(),
        slots_available__gt=0
    ).select_related('guide', 'guide__user').order_by('date')[:5]
    
    context = {
        'tour': tour,
        'upcoming_availabilities': upcoming_availabilities,
        'has_availability': upcoming_availabilities.exists()
    }
    return render(request, 'tours/tour_detail.html', context)

def tour_booking_options(request, tour_id):
    """
    Show all available booking options for a specific tour.
    """
    tour = get_object_or_404(Tour.objects.select_related('park'), pk=tour_id)
    
    # Get all future availabilities for this tour
    availabilities = Availability.objects.filter(
        tour=tour,
        date__gte=timezone.now().date()
    ).select_related('guide', 'guide__user').order_by('date')
    
    # Separate available and fully booked
    available_slots = availabilities.filter(slots_available__gt=0)
    fully_booked = availabilities.filter(slots_available=0)
    
    # Pagination
    paginator = Paginator(available_slots, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tour': tour,
        'page_obj': page_obj,
        'available_slots': page_obj,
        'fully_booked': fully_booked,
        'total_available': available_slots.count(),
        'total_booked': fully_booked.count(),
    }
    return render(request, 'tours/tour_booking_options.html', context)