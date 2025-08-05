# In tours/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count, Min, Max, Sum, Avg
import json
from .models import Tour, Park, Guide, TourCompany
# Import views from additional_views.py
from .additional_views import guide_detail, company_detail
from booking.models import Availability, Booking
from booking.forms import AvailabilitySearchForm
from .forms import TourForm, ParkForm, AvailabilityForm
from collections import defaultdict


def can_manage_parks(user):
    """Check if user can manage parks (UWA Staff only)"""
    if not user.is_authenticated:
        return False
    try:
        profile = user.profile
        return profile.is_staff()
    except:
        return False

def can_manage_tours(user):
    """Check if user can manage tours (Tour Operators or UWA Staff)"""
    return user.is_authenticated and (user.is_staff or (hasattr(user, 'profile') and (user.profile.is_operator() or user.profile.is_staff())))

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


# Park Management Views (UWA Staff only)

def park_list(request):
    """Public park list view"""
    parks = Park.objects.prefetch_related('tours').annotate(
        tour_count=Count('tours'),
        min_price=Min('tours__price'),
        max_price=Max('tours__price')
    ).order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        parks = parks.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Calculate total tours across all parks
    total_tours = sum(park.tour_count for park in parks)
    
    # Check if user can manage parks
    user_can_manage = request.user.is_authenticated and can_manage_parks(request.user)
    
    context = {
        'parks': parks,
        'search_query': search_query,
        'total_tours': total_tours,
        'user_can_manage': user_can_manage,
        'is_management_view': False,  # This is the public view
    }
    
    return render(request, 'tours/park_list.html', context)


@user_passes_test(can_manage_parks, login_url='tours:tour_list')
@user_passes_test(can_manage_parks, login_url='tours:tour_list')
def manage_parks(request):
    """Park management dashboard for UWA Staff only"""
    search_query = request.GET.get('search', '')
    
    parks = Park.objects.prefetch_related('tours').annotate(
        tour_count=Count('tours'),
        min_price=Min('tours__price'),
        max_price=Max('tours__price'),
        total_bookings=Count('tours__availability__bookings')
    ).order_by('name')
    
    # Apply search filter
    if search_query:
        parks = parks.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Calculate total tours across all parks
    total_tours = sum(park.tour_count for park in parks)
    
    context = {
        'parks': parks,
        'search_query': search_query,
        'total_tours': total_tours,
        'user_can_manage': True,
        'is_management_view': True,  # This is the management view
        'total_parks': parks.count(),
    }
    return render(request, 'tours/park_list.html', context)


@user_passes_test(can_manage_parks, login_url='tours:tour_list')
def add_park(request):
    """Add new park"""
    from .forms import ParkForm
    
    if request.method == 'POST':
        form = ParkForm(request.POST, request.FILES)
        if form.is_valid():
            park = form.save()
            messages.success(request, f'Park "{park.name}" has been created successfully!')
            return redirect('tours:manage_parks')
    else:
        form = ParkForm()
    
    context = {
        'form': form,
        'action': 'Add',
        'title': 'Add New Park'
    }
    return render(request, 'tours/park_form.html', context)


@user_passes_test(can_manage_parks, login_url='tours:tour_list')
def edit_park(request, park_id):
    """Edit existing park"""
    from .forms import ParkForm
    
    park = get_object_or_404(Park, id=park_id)
    
    if request.method == 'POST':
        form = ParkForm(request.POST, request.FILES, instance=park)
        if form.is_valid():
            park = form.save()
            messages.success(request, f'Park "{park.name}" has been updated successfully!')
            return redirect('tours:manage_parks')
    else:
        form = ParkForm(instance=park)
    
    context = {
        'form': form,
        'park': park,
        'action': 'Edit',
        'title': f'Edit {park.name}'
    }
    return render(request, 'tours/park_form.html', context)


@user_passes_test(can_manage_parks, login_url='tours:tour_list')
def delete_park(request, park_id):
    """Delete park (AJAX endpoint)"""
    if request.method == 'POST':
        park = get_object_or_404(Park, id=park_id)
        
        # Check if park has tours
        tour_count = park.tours.count()
        if tour_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete park "{park.name}" because it has {tour_count} tour(s) associated with it. Please delete or move the tours first.'
            })
        
        park_name = park.name
        park.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Park "{park_name}" has been deleted successfully.'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def park_detail(request, park_id):
    """Detailed park view with tours - accessible to all users"""
    park = get_object_or_404(Park, id=park_id)
    
    # Get park tours with statistics
    tours = Tour.objects.filter(park=park).annotate(
        availability_count=Count('availability'),
        booking_count=Count('availability__bookings'),
        total_revenue=Sum('availability__bookings__total_cost')
    ).order_by('name')
    
    # Get park statistics
    total_tours = tours.count()
    total_bookings = sum(tour.booking_count or 0 for tour in tours)
    total_revenue = sum(tour.total_revenue or 0 for tour in tours)
    
    # Calculate price range
    prices = [tour.price for tour in tours if tour.price]
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    
    context = {
        'park': park,
        'tours': tours,
        'total_tours': total_tours,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'tours/park_detail_public.html', context)


# Redirect old management URLs to public ones
def park_detail_redirect(request, park_id):
    """Redirect old management park detail URLs to public park detail"""
    return redirect('tours:park_detail', park_id=park_id)


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def manage_tours(request):
    """Tour management dashboard"""
    search_query = request.GET.get('search', '')
    park_filter = request.GET.get('park', '')
    company_filter = request.GET.get('company', '')
    
    tours = Tour.objects.select_related('park', 'company')
    
    # Filter tours based on user role
    if not request.user.is_superuser and hasattr(request.user, 'profile'):
        profile = request.user.profile
        
        if profile.is_operator() and profile.is_staff():
            # User has both operator and staff roles - show their company tours and UWA tours
            from django.db.models import Q
            tours = tours.filter(
                Q(company__operators=request.user) | 
                Q(company__is_uwa=True)
            )
        elif profile.is_operator():
            # Regular operators only see tours from their companies
            tours = tours.filter(company__operators=request.user)
        elif profile.is_staff():
            # UWA staff only see UWA tours
            tours = tours.filter(company__is_uwa=True)
        else:
            # Regular users don't see any tours in management
            tours = tours.none()
    
    # Apply search filter
    if search_query:
        tours = tours.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(park__name__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )
    
    # Apply park filter
    if park_filter:
        tours = tours.filter(park_id=park_filter)
        
    # Apply company filter
    if company_filter:
        tours = tours.filter(company_id=company_filter)
    
    # Get tour statistics
    tours = tours.annotate(
        availability_count=Count('availability'),
        booking_count=Count('availability__bookings')
    ).order_by('park__name', 'name')
    
    # Get all parks for filter dropdown
    parks = Park.objects.all().order_by('name')
    
    # Get companies for filter dropdown
    from .models import TourCompany
    if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_staff()):
        # Admin and UWA staff see all companies
        companies = TourCompany.objects.all().order_by('name')
    elif hasattr(request.user, 'profile') and request.user.profile.is_operator():
        # Operators only see their companies
        companies = TourCompany.objects.filter(operators=request.user).order_by('name')
    else:
        companies = TourCompany.objects.none()
    
    # Calculate statistics only on the filtered tours the user can access
    average_price = tours.aggregate(avg_price=Avg('price'))['avg_price'] or 0
    average_duration = tours.aggregate(avg_duration=Avg('duration_hours'))['avg_duration'] or 0
    
    # Paginate results
    paginator = Paginator(tours, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if user can manage parks
    user_can_manage_parks = request.user.is_authenticated and can_manage_parks(request.user)
    
    context = {
        'tours': tours,  # For template compatibility
        'page_obj': page_obj,
        'search_query': search_query,
        'park_filter': park_filter,
        'company_filter': company_filter,
        'parks': parks,
        'companies': companies,
        'total_tours': tours.count(),
        'average_price': average_price,
        'average_duration': average_duration,
        'user_can_manage_parks': user_can_manage_parks,
    }
    return render(request, 'tours/manage_tours.html', context)


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def add_tour(request):
    """Add new tour"""
    from .forms import TourForm
    from .models import TourCompany
    
    # Create UWA company if it doesn't exist yet
    uwa_company, created = TourCompany.objects.get_or_create(
        name="Uganda Wildlife Authority",
        defaults={
            'is_uwa': True,
            'description': "Official tours offered by the Uganda Wildlife Authority",
        }
    )
    
    # If user has no company and is an operator, create one for them
    if hasattr(request.user, 'profile') and request.user.profile.is_operator():
        profile = request.user.profile
        if profile.operator_company_name and not TourCompany.objects.filter(operators=request.user).exists():
            company, created = TourCompany.objects.get_or_create(
                name=profile.operator_company_name,
                defaults={
                    'license_number': profile.operator_license_number or '',
                    'website': profile.operator_website or '',
                    'is_uwa': False,
                }
            )
            if created:
                company.operators.add(request.user)
    
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.created_by = request.user
            tour.save()
            messages.success(request, f'Tour "{tour.name}" has been created successfully!')
            return redirect('tours:manage_tours')
    else:
        form = TourForm(user=request.user)
    
    context = {
        'form': form,
        'action': 'Add',
        'title': 'Add New Tour'
    }
    return render(request, 'tours/tour_form.html', context)


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def edit_tour(request, tour_id):
    """Edit existing tour with availability management"""
    from .forms import TourForm
    
    tour = get_object_or_404(Tour, id=tour_id)
    
    # Check if user has permission to edit this tour
    if not request.user.is_superuser and hasattr(request.user, 'profile'):
        profile = request.user.profile
        
        if profile.is_operator() and profile.is_staff():
            # Users with both operator and staff roles can edit:
            # 1. Tours from their own companies
            # 2. UWA tours
            if not (tour.company.operators.filter(id=request.user.id).exists() or tour.company.is_uwa):
                messages.error(request, "You don't have permission to edit this tour.")
                return redirect('tours:manage_tours')
        elif profile.is_operator():
            # Regular operators can only edit their own tours
            if not tour.company.operators.filter(id=request.user.id).exists():
                messages.error(request, "You don't have permission to edit this tour.")
                return redirect('tours:manage_tours')
        elif profile.is_staff():
            # UWA staff can only edit UWA tours
            if not tour.company.is_uwa:
                messages.error(request, "As UWA staff, you can only edit UWA tours.")
                return redirect('tours:manage_tours')
    
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour, user=request.user)
        if form.is_valid():
            tour = form.save()
            messages.success(request, f'Tour "{tour.name}" has been updated successfully!')
            return redirect('tours:edit_tour', tour_id=tour.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TourForm(instance=tour)
    
    # Get availability data
    availabilities = Availability.objects.filter(tour=tour).select_related('guide', 'guide__user').order_by('date')
    upcoming_availabilities = availabilities.filter(date__gte=timezone.now().date())
    past_availabilities = availabilities.filter(date__lt=timezone.now().date())
    
    # Get available guides
    from tours.models import Guide
    guides = Guide.objects.select_related('user').all()
    
    context = {
        'form': form,
        'tour': tour,
        'action': 'Edit',
        'title': f'Edit {tour.name}',
        'upcoming_availabilities': upcoming_availabilities,
        'past_availabilities': past_availabilities,
        'guides': guides,
    }
    return render(request, 'tours/tour_edit_enhanced.html', context)


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def delete_tour(request, tour_id):
    """Delete tour (AJAX endpoint)"""
    if request.method == 'POST':
        tour = get_object_or_404(Tour, id=tour_id)
        
        # Check if tour has bookings
        booking_count = Booking.objects.filter(availability__tour=tour).count()
        if booking_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete tour "{tour.name}" because it has {booking_count} booking(s). Please cancel or complete the bookings first.'
            })
        
        tour_name = tour.name
        tour.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Tour "{tour_name}" has been deleted successfully.'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
@login_required
def add_availability(request, tour_id):
    """Add new availability for a tour"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            tour = get_object_or_404(Tour, id=tour_id)
            guide_id = data.get('guide_id')
            guide = None
            if guide_id:
                guide = get_object_or_404(Guide, id=guide_id)
            
            availability = Availability.objects.create(
                tour=tour,
                date=data['date'],
                slots_available=data['slots_available'],
                guide=guide
            )
            
            return JsonResponse({
                'success': True,
                'availability': {
                    'id': availability.id,
                    'date': availability.date.strftime('%Y-%m-%d'),
                    'slots_available': availability.slots_available,
                    'guide_name': availability.guide.user.get_full_name() if availability.guide else 'No guide assigned',
                    'bookings_count': 0
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def edit_availability(request, availability_id):
    """Edit existing availability"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            availability = get_object_or_404(Availability, id=availability_id)
            
            guide_id = data.get('guide_id')
            guide = None
            if guide_id:
                guide = get_object_or_404(Guide, id=guide_id)
            
            availability.date = data['date']
            availability.slots_available = data['slots_available']
            availability.guide = guide
            availability.save()
            
            return JsonResponse({
                'success': True,
                'availability': {
                    'id': availability.id,
                    'date': availability.date.strftime('%Y-%m-%d'),
                    'slots_available': availability.slots_available,
                    'guide_name': availability.guide.user.get_full_name() if availability.guide else 'No guide assigned'
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def delete_availability(request, availability_id):
    """Delete availability"""
    if request.method == 'DELETE':
        try:
            availability = get_object_or_404(Availability, id=availability_id)
            
            # Check company-based permissions
            if not request.user.is_superuser and hasattr(request.user, 'profile'):
                profile = request.user.profile
                tour_company = availability.tour.company
                
                # Users with both operator and staff roles
                if profile.is_operator() and profile.is_staff():
                    # Can delete their company's availabilities and UWA availabilities
                    if not (tour_company.is_uwa or tour_company.operators.filter(id=request.user.id).exists()):
                        return JsonResponse({'success': False, 'error': "You can only delete availabilities from your own company or UWA."})
                        
                # Regular UWA staff can only delete UWA tour availabilities
                elif profile.is_staff():
                    if not tour_company.is_uwa:
                        return JsonResponse({'success': False, 'error': "As UWA staff, you can only delete UWA tour availabilities."})
                        
                # Tour operators can only delete their own companies' tour availabilities
                elif profile.is_operator():
                    if not tour_company.operators.filter(id=request.user.id).exists():
                        return JsonResponse({'success': False, 'error': "You can only delete availabilities from your own company."})
            
            availability.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def manage_availability(request):
    """
    Main page for managing tour availabilities/dates
    Allows tour operators and UWA staff to manage all tour dates in one place
    """
    # Get all availabilities for the current user's tours
    availabilities = Availability.objects.select_related('tour', 'tour__company')
    
    # Filter availabilities based on user role
    if not request.user.is_superuser and hasattr(request.user, 'profile'):
        profile = request.user.profile
        
        if profile.is_operator() and profile.is_staff():
            # User has both operator and staff roles - show their company tours and UWA tours
            from django.db.models import Q
            availabilities = availabilities.filter(
                Q(tour__company__operators=request.user) | 
                Q(tour__company__is_uwa=True)
            )
        elif profile.is_operator():
            # Regular operators only see availabilities from their companies
            availabilities = availabilities.filter(tour__company__operators=request.user)
        elif profile.is_staff():
            # UWA staff only see UWA tour availabilities
            availabilities = availabilities.filter(tour__company__is_uwa=True)
        else:
            # Regular users don't see any availabilities in management
            availabilities = availabilities.none()
    
    # Apply filters
    tour_filter = request.GET.get('tour', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    guide_filter = request.GET.get('guide', '')
    availability_filter = request.GET.get('availability', '')
    
    if tour_filter:
        availabilities = availabilities.filter(tour_id=tour_filter)
    
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            availabilities = availabilities.filter(date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            availabilities = availabilities.filter(date__lte=date_to)
        except ValueError:
            pass
    
    if guide_filter:
        availabilities = availabilities.filter(guide_id=guide_filter)
    
    if availability_filter:
        if availability_filter == 'available':
            availabilities = availabilities.filter(slots_available__gt=0)
        elif availability_filter == 'booked':
            availabilities = availabilities.filter(slots_available=0)
    
    # Order by date
    availabilities = availabilities.select_related('tour', 'tour__park', 'guide', 'guide__user').order_by('date')
    
    # Get statistics
    total_availabilities = availabilities.count()
    total_available = availabilities.filter(slots_available__gt=0).count()
    total_booked = availabilities.filter(slots_available=0).count()
    
    # Get tours and guides for filters, filtered by company access
    if request.user.is_superuser:
        # Superuser sees all tours
        tours = Tour.objects.all().order_by('name')
    elif hasattr(request.user, 'profile'):
        profile = request.user.profile
        
        if profile.is_operator() and profile.is_staff():
            # User has both operator and staff roles - show their company tours and UWA tours
            from django.db.models import Q
            tours = Tour.objects.filter(
                Q(company__operators=request.user) | 
                Q(company__is_uwa=True)
            ).order_by('name')
        elif profile.is_operator():
            # Regular operators only see their companies' tours
            tours = Tour.objects.filter(company__operators=request.user).order_by('name')
        elif profile.is_staff():
            # UWA staff only see UWA tours
            tours = Tour.objects.filter(company__is_uwa=True).order_by('name')
        else:
            # Regular users don't see any tours
            tours = Tour.objects.none()
    else:
        # Non-authenticated users see no tours
        tours = Tour.objects.none()
        
    guides = Guide.objects.select_related('user').all().order_by('user__first_name')
    
    # Pagination
    paginator = Paginator(availabilities, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Create form for adding new availability
    if request.method == 'POST':
        print("POST request received in manage_availability")
        print("POST data:", request.POST)
        form = AvailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            print("Form is valid. Saving...")
            availability = form.save()
            messages.success(request, f'New date added for {availability.tour.name} on {availability.date}')
            return redirect('tours:manage_availability')
        else:
            print("Form validation errors:", form.errors)
    else:
        form = AvailabilityForm(user=request.user)
    
    context = {
        'page_obj': page_obj,
        'total_availabilities': total_availabilities,
        'total_available': total_available,
        'total_booked': total_booked,
        'tours': tours,
        'guides': guides,
        'form': form,
        'tour_filter': tour_filter,
        'date_from': date_from,
        'date_to': date_to,
        'guide_filter': guide_filter,
        'availability_filter': availability_filter,
        'user_can_manage': True,  # Always true for management view
        'is_management_view': True,  # Flag to show management-specific features
    }
    
    return render(request, 'tours/public_availability_list.html', context)


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def add_availability_page(request):
    """Add availability using the dedicated form page"""
    # Check if user has permission
    if not request.user.is_superuser and not hasattr(request.user, 'profile'):
        messages.error(request, "You don't have permission to add availability.")
        return redirect('tours:manage_availability')
        
    if not request.user.is_superuser and not request.user.profile.is_staff() and not request.user.profile.is_operator():
        messages.error(request, "You don't have permission to add availability.")
        return redirect('tours:manage_availability')
    
    # For operators, check if they have any companies
    if not request.user.is_superuser and hasattr(request.user, 'profile') and request.user.profile.is_operator():
        from .models import TourCompany
        if not TourCompany.objects.filter(operators=request.user).exists():
            messages.error(request, "You don't have any tour companies associated with your account. Please contact an administrator.")
            return redirect('tours:manage_availability')
    
    if request.method == 'POST':
        form = AvailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            new_availability = form.save()
            messages.success(request, f'New availability for {new_availability.tour.name} on {new_availability.date} has been added.')
            return redirect('tours:manage_availability')
    else:
        form = AvailabilityForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Add New Tour Date',
        'action': 'Add',
    }
    
    return render(request, 'tours/availability_form.html', context)


@user_passes_test(can_manage_tours, login_url='tours:tour_list')
def edit_availability_form(request, availability_id):
    """Edit availability using the new form"""
    availability = get_object_or_404(Availability, id=availability_id)
    
    # Check basic permission requirements
    if not request.user.is_superuser and not hasattr(request.user, 'profile'):
        messages.error(request, "You don't have permission to edit this availability.")
        return redirect('tours:manage_availability')
        
    if not request.user.is_superuser and not request.user.profile.is_staff() and not request.user.profile.is_operator():
        messages.error(request, "You don't have permission to edit this availability.")
        return redirect('tours:manage_availability')
    
    # Check company-based permissions
    if not request.user.is_superuser and hasattr(request.user, 'profile'):
        profile = request.user.profile
        tour_company = availability.tour.company
        
        # Users with both operator and staff roles
        if profile.is_operator() and profile.is_staff():
            # Can edit their company's availabilities and UWA availabilities
            if not (tour_company.is_uwa or tour_company.operators.filter(id=request.user.id).exists()):
                messages.error(request, "You can only edit availabilities from your own company or UWA.")
                return redirect('tours:manage_availability')
                
        # Regular UWA staff can only edit UWA tour availabilities
        elif profile.is_staff():
            if not tour_company.is_uwa:
                messages.error(request, "As UWA staff, you can only edit UWA tour availabilities.")
                return redirect('tours:manage_availability')
                
        # Tour operators can only edit their own companies' tour availabilities
        elif profile.is_operator():
            if not tour_company.operators.filter(id=request.user.id).exists():
                messages.error(request, "You can only edit availabilities from your own company.")
                return redirect('tours:manage_availability')
    
    if request.method == 'POST':
        form = AvailabilityForm(request.POST, instance=availability, user=request.user)
        if form.is_valid():
            updated_availability = form.save()
            messages.success(request, f'Availability for {updated_availability.tour.name} on {updated_availability.date} has been updated.')
            return redirect('tours:manage_availability')
    else:
        form = AvailabilityForm(instance=availability, user=request.user)
    
    context = {
        'form': form,
        'availability': availability,
        'title': f'Edit Availability - {availability.tour.name} on {availability.date}',
        'action': 'Edit',
    }
    
    return render(request, 'tours/availability_form.html', context)


def public_availability_list(request):
    """
    Public page for viewing tour availabilities/dates
    Shows the same information as manage_availability but with management buttons only for authorized users
    """
    # Get all availabilities (future dates only for public view)
    availabilities = Availability.objects.select_related('tour', 'tour__company', 'tour__park').filter(
        date__gte=timezone.now().date()  # Only show future dates for public view
    )
    
    # Apply filters
    tour_filter = request.GET.get('tour', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    guide_filter = request.GET.get('guide', '')
    availability_filter = request.GET.get('availability', '')
    park_filter = request.GET.get('park', '')
    
    if tour_filter:
        availabilities = availabilities.filter(tour_id=tour_filter)
    
    if park_filter:
        availabilities = availabilities.filter(tour__park_id=park_filter)
    
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            availabilities = availabilities.filter(date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            availabilities = availabilities.filter(date__lte=date_to)
        except ValueError:
            pass
    
    if guide_filter:
        if guide_filter == 'none':
            availabilities = availabilities.filter(guide__isnull=True)
        else:
            availabilities = availabilities.filter(guide_id=guide_filter)
    
    if availability_filter:
        if availability_filter == 'available':
            availabilities = availabilities.filter(slots_available__gt=0)
        elif availability_filter == 'booked':
            availabilities = availabilities.filter(slots_available=0)
    
    # Order by date
    availabilities = availabilities.order_by('date')
    
    # Get statistics
    total_availabilities = availabilities.count()
    total_available = availabilities.filter(slots_available__gt=0).count()
    total_booked = availabilities.filter(slots_available=0).count()
    
    # Get tours, parks and guides for filters
    tours = Tour.objects.all().order_by('name')
    parks = Park.objects.all().order_by('name')
    guides = Guide.objects.select_related('user').all().order_by('user__first_name')
    
    # Check if user can manage availabilities
    user_can_manage = request.user.is_authenticated and can_manage_tours(request.user)
    
    # Pagination
    paginator = Paginator(availabilities, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_availabilities': total_availabilities,
        'total_available': total_available,
        'total_booked': total_booked,
        'tours': tours,
        'parks': parks,
        'guides': guides,
        'tour_filter': tour_filter,
        'park_filter': park_filter,
        'date_from': date_from,
        'date_to': date_to,
        'guide_filter': guide_filter,
        'availability_filter': availability_filter,
        'user_can_manage': user_can_manage,
    }
    
    return render(request, 'tours/public_availability_list.html', context)