from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import UserEditForm, ProfileEditForm, PasswordChangeForm
from .models import Profile, Wishlist

class CustomLoginView(LoginView):
    """Custom login view with modern template"""
    template_name = 'accounts/login_modern.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to next parameter or default to tour list"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('tours:tour_list')

def signup(request):
    """User registration view with modern template"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set first and last name if provided
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            login(request, user)
            messages.success(request, 'Welcome to UWA Wildlife Tours! Your account has been created successfully.')
            
            # Redirect to next parameter or default to tour list
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('tours:tour_list')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup_modern.html', {'form': form})

@login_required
def profile(request):
    """Enhanced user profile view with statistics and recent activity"""
    from django.db.models import Count, Sum, Q
    from booking.models import Booking
    from tours.models import Park
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    user = request.user
    
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Calculate statistics
    total_bookings = user.bookings.count()
    confirmed_bookings = user.bookings.filter(booking_status='confirmed').count()
    completed_bookings = user.bookings.filter(booking_status='completed').count()
    
    # Calculate total spent
    total_spent = user.bookings.filter(
        booking_status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
    
    # Calculate parks visited (from confirmed/completed bookings)
    parks_visited = Park.objects.filter(
        tours__availability__bookings__tourist=user,
        tours__availability__bookings__booking_status__in=['confirmed', 'completed']
    ).distinct().count()
    
    # Calculate people brought (total from all bookings)
    people_brought = user.bookings.filter(
        booking_status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('num_of_people'))['total'] or 0
    
    # Get recent activity (last 10 bookings)
    recent_bookings = user.bookings.select_related(
        'availability__tour__park', 'availability__guide__user'
    ).order_by('-booking_date')[:10]
    
    # Calculate adventure level based on bookings
    if completed_bookings >= 20:
        adventure_level = "Explorer Legend"
    elif completed_bookings >= 10:
        adventure_level = "Wildlife Expert"
    elif completed_bookings >= 5:
        adventure_level = "Adventure Enthusiast"
    elif completed_bookings >= 1:
        adventure_level = "Wildlife Explorer"
    else:
        adventure_level = "Future Explorer"
    
    # Conservation impact (estimated based on bookings) - using Decimal for precision
    conservation_contribution = total_spent * Decimal('0.1')  # Assume 10% goes to conservation
    trees_planted = completed_bookings * 2  # Assume 2 trees per completed tour
    
    # Mock notification system - calculate unread notifications
    # In a real system, you'd have a Notification model
    unread_notifications = 0
    
    # Check for upcoming tours (notifications for tours in next 7 days)
    from datetime import date
    upcoming_tours = user.bookings.filter(
        booking_status='confirmed',
        availability__date__gte=date.today(),
        availability__date__lte=date.today() + timedelta(days=7)
    ).count()
    unread_notifications += upcoming_tours
    
    # Check for recent booking confirmations (last 30 days)
    recent_confirmations = user.bookings.filter(
        booking_status='confirmed',
        booking_date__gte=datetime.now() - timedelta(days=30)
    ).count()
    unread_notifications += min(recent_confirmations, 3)  # Cap at 3 to avoid too many notifications
    
    # Add some promotional notifications (mock)
    if total_bookings == 0:
        unread_notifications += 1  # Welcome/first booking discount
    elif completed_bookings > 0 and completed_bookings % 5 == 0:
        unread_notifications += 1  # Milestone achievement notification
    
    context = {
        'profile': profile,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,
        'total_spent': total_spent,
        'parks_visited': parks_visited,
        'people_brought': people_brought,
        'recent_bookings': recent_bookings,
        'adventure_level': adventure_level,
        'conservation_contribution': conservation_contribution,
        'trees_planted': trees_planted,
        'unread_notifications': unread_notifications,
        'upcoming_tours': upcoming_tours,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile view"""
    # Get or create profile for the user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def change_password(request):
    """Change user password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Important to keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def notification_settings(request):
    """Notification settings view"""
    from .models import NotificationSettings
    
    # Get or create notification settings for the user
    settings, created = NotificationSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update notification preferences
        settings.email_bookings = request.POST.get('email_bookings') == 'on'
        settings.email_promotions = request.POST.get('email_promotions') == 'on'
        settings.email_reminders = request.POST.get('email_reminders') == 'on'
        settings.email_updates = request.POST.get('email_updates') == 'on'
        settings.sms_reminders = request.POST.get('sms_reminders') == 'on'
        settings.save()
        
        messages.success(request, 'Your notification preferences have been updated!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/notification_settings.html', {'settings': settings})

@login_required
def payment_methods(request):
    """Payment methods view"""
    # This is a placeholder for future payment method management
    return render(request, 'accounts/payment_methods.html')

@login_required
def wishlist(request):
    """User wishlist view"""
    from .models import Wishlist
    from tours.models import Tour
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('tour__park')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'accounts/wishlist.html', context)

def add_to_wishlist(request, tour_id):
    """Add tour to wishlist"""
    from django.http import JsonResponse
    from django.urls import reverse
    
    # Check if user is authenticated for AJAX requests
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Content-Type', ''):
            login_url = reverse('accounts:login')
            return JsonResponse({
                'success': False,
                'message': 'Please log in to add tours to your wishlist.',
                'redirect_url': f"{login_url}?next={request.get_full_path()}"
            }, status=401)
        else:
            login_url = reverse('accounts:login')
            return redirect(f"{login_url}?next={request.get_full_path()}")
    
    if request.method == 'POST':
        try:
            from .models import Wishlist
            from tours.models import Tour
            
            tour = Tour.objects.get(id=tour_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                tour=tour
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'{tour.name} added to your wishlist!',
                    'action': 'added'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': f'{tour.name} is already in your wishlist.',
                    'action': 'exists'
                })
        except Tour.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Tour not found.'
            })
        except Exception as e:
            print(f"Wishlist error: {e}")  # Debug
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def remove_from_wishlist(request, tour_id):
    """Remove tour from wishlist"""
    from django.urls import reverse
    
    # Check if user is authenticated for AJAX requests
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Content-Type', ''):
            login_url = reverse('accounts:login')
            return JsonResponse({
                'success': False,
                'message': 'Please log in to manage your wishlist.',
                'redirect_url': f"{login_url}?next={request.get_full_path()}"
            }, status=401)
        else:
            login_url = reverse('accounts:login')
            return redirect(f"{login_url}?next={request.get_full_path()}")
    
    if request.method == 'POST':
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, tour_id=tour_id)
            tour_name = wishlist_item.tour.name
            wishlist_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{tour_name} removed from your wishlist!',
                'action': 'removed'
            })
        except Wishlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Item not found in wishlist.'
            })
        except Exception as e:
            print(f"Remove wishlist error: {e}")  # Debug
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def help_support(request):
    """Help and support view"""
    return render(request, 'accounts/help_support.html')

@login_required
def notifications_page(request):
    """Full notifications page view"""
    return render(request, 'accounts/notifications.html')

@login_required
def get_notifications(request):
    """Get user notifications for dropdown"""
    try:
        from datetime import datetime, timedelta
        from booking.models import Booking
        
        notifications = []
        user = request.user
        
        # 1. Upcoming tours (next 7 days)
        upcoming_bookings = user.bookings.filter(
            booking_status='confirmed',
            availability__date__gte=datetime.now().date(),
            availability__date__lte=datetime.now().date() + timedelta(days=7)
        ).select_related('availability__tour', 'availability__tour__park')
        
        for booking in upcoming_bookings:
            notifications.append({
                'id': f'upcoming_{booking.id}',
                'type': 'upcoming',
                'title': f'Upcoming Tour: {booking.availability.tour.name}',
                'message': f'Your tour is scheduled for {booking.availability.date.strftime("%B %d, %Y")}',
                'time': 'Upcoming',
                'icon': 'calendar-check',
                'color': 'text-orange-600',
                'bg_color': 'bg-orange-50',
                'url': f'/booking/my-bookings/'
            })
        
        # 2. Recent booking confirmations (last 30 days)
        recent_confirmations = user.bookings.filter(
            booking_status='confirmed',
            booking_date__gte=datetime.now() - timedelta(days=30)
        ).select_related('availability__tour').order_by('-booking_date')[:3]
        
        for booking in recent_confirmations:
            days_ago = (datetime.now().date() - booking.booking_date.date()).days
            time_text = 'Today' if days_ago == 0 else f'{days_ago} day{"s" if days_ago > 1 else ""} ago'
            
            notifications.append({
                'id': f'confirmed_{booking.id}',
                'type': 'confirmation',
                'title': 'Booking Confirmed',
                'message': f'{booking.availability.tour.name} has been confirmed',
                'time': time_text,
                'icon': 'check-circle',
                'color': 'text-green-600',
                'bg_color': 'bg-green-50',
                'url': f'/booking/my-bookings/'
            })
        
        # 3. Welcome message for new users
        total_bookings = user.bookings.count()
        if total_bookings == 0:
            notifications.append({
                'id': 'welcome',
                'type': 'welcome',
                'title': 'Welcome to UWA Wildlife Tours!',
                'message': 'Get 10% off your first booking with code WELCOME10',
                'time': 'New',
                'icon': 'gift',
                'color': 'text-blue-600',
                'bg_color': 'bg-blue-50',
                'url': '/tours/'
            })
        
        # 4. Achievement notifications
        completed_bookings = user.bookings.filter(booking_status='completed').count()
        if completed_bookings > 0 and completed_bookings % 5 == 0:
            notifications.append({
                'id': f'achievement_{completed_bookings}',
                'type': 'achievement',
                'title': f'Achievement Unlocked!',
                'message': f'You\'ve completed {completed_bookings} tours! You\'re a true wildlife explorer.',
                'time': 'New',
                'icon': 'award',
                'color': 'text-purple-600',
                'bg_color': 'bg-purple-50',
                'url': '/accounts/profile/'
            })
        
        # Sort notifications by type priority and limit to 10
        type_priority = {'upcoming': 1, 'confirmation': 2, 'achievement': 3, 'welcome': 4}
        notifications.sort(key=lambda x: type_priority.get(x['type'], 5))
        notifications = notifications[:10]  # Limit to 10 notifications
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_notifications: {str(e)}")
        
        # Return error response
        return JsonResponse({
            'success': False,
            'error': str(e),
            'notifications': [],
            'count': 0
        })
