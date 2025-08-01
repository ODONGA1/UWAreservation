# In tours/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count, Min, Max, Sum, Avg
from .models import Tour
from booking.models import Availability, Booking
from booking.forms import AvailabilitySearchForm
from collections import defaultdict

def tour_list(request):
    """
    Modern tour list view with enhanced search and filtering.
    Groups tours together and shows aggregate availability information.
    """
    form = AvailabilitySearchForm(request.GET or None)
    
    # Get all availabilities with upcoming dates
    availabilities = Availability.objects.filter(
        date__gte=timezone.now().date(),
        slots_available__gt=0
    ).select_related('tour', 'tour__park', 'guide', 'guide__user').order_by('date')
    
    # Apply search filters
    if form.is_valid():
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        park = form.cleaned_data.get('park')
        guide = form.cleaned_data.get('guide')
        min_slots = form.cleaned_data.get('min_slots')
        price_range = form.cleaned_data.get('price_range')
        duration = form.cleaned_data.get('duration')
        search_query = form.cleaned_data.get('search_query')
        
        # Date filters
        if date_from:
            availabilities = availabilities.filter(date__gte=date_from)
        if date_to:
            availabilities = availabilities.filter(date__lte=date_to)
            
        # Park filter
        if park:
            availabilities = availabilities.filter(tour__park=park)
            
        # Guide filter
        if guide:
            availabilities = availabilities.filter(guide=guide)
            
        # Minimum slots filter
        if min_slots:
            availabilities = availabilities.filter(slots_available__gte=min_slots)
            
        # Price range filter
        if price_range:
            if price_range == '0-100':
                availabilities = availabilities.filter(tour__price__lt=100)
            elif price_range == '100-200':
                availabilities = availabilities.filter(tour__price__gte=100, tour__price__lt=200)
            elif price_range == '200-500':
                availabilities = availabilities.filter(tour__price__gte=200, tour__price__lt=500)
            elif price_range == '500+':
                availabilities = availabilities.filter(tour__price__gte=500)
                
        # Duration filter
        if duration:
            if duration == '0-4':
                availabilities = availabilities.filter(tour__duration_hours__lt=4)
            elif duration == '4-8':
                availabilities = availabilities.filter(tour__duration_hours__gte=4, tour__duration_hours__lte=8)
            elif duration == '8+':
                availabilities = availabilities.filter(tour__duration_hours__gt=8)
                
        # Search query filter
        if search_query:
            availabilities = availabilities.filter(
                Q(tour__name__icontains=search_query) |
                Q(tour__description__icontains=search_query) |
                Q(tour__park__name__icontains=search_query) |
                Q(tour__park__location__icontains=search_query) |
                Q(guide__specialization__icontains=search_query) |
                Q(guide__user__first_name__icontains=search_query) |
                Q(guide__user__last_name__icontains=search_query)
            )
    
    # Group availabilities by tour and calculate aggregate data
    tour_data = {}
    for availability in availabilities:
        tour_id = availability.tour.id
        if tour_id not in tour_data:
            # Calculate booking statistics for this tour
            tour_bookings = Booking.objects.filter(availability__tour_id=tour_id)
            
            # Current active bookings (confirmed and pending)
            current_bookings = tour_bookings.filter(
                booking_status__in=['confirmed', 'pending'],
                availability__date__gte=timezone.now().date()
            ).count()
            
            # Total completed tours
            completed_tours = tour_bookings.filter(
                booking_status='completed'
            ).count()
            
            # Calculate average rating (mock for now - you can implement a rating system later)
            # For now, we'll use a calculated rating based on popularity and completion rate
            total_bookings = tour_bookings.count()
            if total_bookings > 0:
                completion_rate = completed_tours / total_bookings
                # Base rating of 4.0, adjusted by completion rate and popularity
                calculated_rating = 4.0 + (completion_rate * 0.8) + min(total_bookings / 100, 0.8)
                calculated_rating = min(calculated_rating, 5.0)  # Cap at 5.0
            else:
                calculated_rating = 4.2  # Default rating for new tours
            
            tour_data[tour_id] = {
                'tour': availability.tour,
                'availabilities': [],
                'total_dates': 0,
                'earliest_date': availability.date,
                'latest_date': availability.date,
                'total_slots': 0,
                'guides': set(),
                'sample_availability': availability,
                'current_bookings': current_bookings,
                'completed_tours': completed_tours,
                'rating': round(calculated_rating, 1)
            }
        
        tour_data[tour_id]['availabilities'].append(availability)
        tour_data[tour_id]['total_dates'] += 1
        tour_data[tour_id]['total_slots'] += availability.slots_available
        
        # Track date range
        if availability.date < tour_data[tour_id]['earliest_date']:
            tour_data[tour_id]['earliest_date'] = availability.date
        if availability.date > tour_data[tour_id]['latest_date']:
            tour_data[tour_id]['latest_date'] = availability.date
            
        # Track unique guides
        if availability.guide:
            tour_data[tour_id]['guides'].add(availability.guide)
    
    # Convert to list and sort by earliest date
    grouped_tours = list(tour_data.values())
    grouped_tours.sort(key=lambda x: x['earliest_date'])
    
    # Get user's wishlist if authenticated
    user_wishlist_tour_ids = set()
    if request.user.is_authenticated:
        try:
            from accounts.models import Wishlist
            user_wishlist_tour_ids = set(
                Wishlist.objects.filter(user=request.user).values_list('tour_id', flat=True)
            )
        except:
            # If Wishlist model doesn't exist or other error, continue without wishlist data
            pass
    
    # Add wishlist information to each tour
    for tour_data_item in grouped_tours:
        tour_data_item['is_in_wishlist'] = tour_data_item['tour'].id in user_wishlist_tour_ids
    
    # Pagination
    paginator = Paginator(grouped_tours, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'grouped_tours': page_obj,
        'page_obj': page_obj,
        'user_wishlist_tour_ids': list(user_wishlist_tour_ids),
    }
    
    # Use modern template
    return render(request, 'tours/tour_list_modern.html', context)

def tour_detail(request, tour_id):
    """
    Modern tour detail view with enhanced booking interface and pagination.
    """
    tour = get_object_or_404(Tour.objects.select_related('park'), pk=tour_id)
    
    # Get base query for all upcoming availabilities
    base_query = Availability.objects.filter(
        tour=tour,
        date__gte=timezone.now().date()
    ).select_related('guide', 'guide__user').order_by('date')
    
    # Handle month filtering
    selected_month = request.GET.get('month', '')
    filtered_availabilities = base_query
    
    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            filtered_availabilities = base_query.filter(
                date__year=year,
                date__month=month
            )
        except (ValueError, TypeError):
            # Invalid month format, use all availabilities
            pass
    
    # Get available months for dropdown
    available_months = base_query.dates('date', 'month', order='ASC')
    
    # Pagination - show 6 dates per page
    from django.core.paginator import Paginator
    paginator = Paginator(filtered_availabilities, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate popularity statistics for all dates (not just filtered ones)
    all_availabilities = base_query
    fully_booked_count = 0
    available_count = 0
    
    for availability in all_availabilities:
        if availability.slots_available == 0:
            fully_booked_count += 1
        else:
            available_count += 1
    
    # Add calculated fields for each availability on current page
    for availability in page_obj:
        # Calculate total spots and booked spots
        total_spots = tour.max_participants
        spots_booked = total_spots - availability.slots_available
        availability.total_spots = total_spots
        availability.spots_booked = spots_booked
        availability.booking_percentage = (spots_booked / total_spots * 100) if total_spots > 0 else 0
    
    context = {
        'tour': tour,
        'upcoming_availabilities': page_obj,
        'page_obj': page_obj,
        'has_availability': all_availabilities.exists(),
        'fully_booked_count': fully_booked_count,
        'available_count': available_count,
        'total_dates': filtered_availabilities.count(),
        'available_months': available_months,
        'selected_month': selected_month,
    }
    
    # Use modern template
    return render(request, 'tours/tour_detail_modern.html', context)

def similar_tours(request, tour_id):
    """
    HTMX endpoint for loading similar tours.
    """
    tour = get_object_or_404(Tour, pk=tour_id)
    
    # Find similar tours in the same park
    similar = Tour.objects.filter(
        park=tour.park
    ).exclude(pk=tour_id).select_related('park')[:3]
    
    # If not enough similar tours, add tours from other parks
    if similar.count() < 3:
        additional = Tour.objects.exclude(
            park=tour.park
        ).exclude(pk=tour_id).select_related('park')[:3 - similar.count()]
        similar = list(similar) + list(additional)
    
    context = {'similar_tours': similar}
    return render(request, 'tours/similar_tours_partial.html', context)

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