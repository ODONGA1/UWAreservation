from datetime import datetime, timedelta
from django.db.models import Count, Q
from booking.models import Booking


def notifications(request):
    """
    Context processor to provide notification count across all templates
    """
    if not request.user.is_authenticated:
        return {'unread_notifications': 0}
    
    # Calculate unread notifications (same logic as profile view)
    unread_notifications = 0
    
    # 1. Check for upcoming tours (next 7 days)
    upcoming_tours = Booking.objects.filter(
        tourist=request.user,
        booking_status='confirmed',
        availability__date__gte=datetime.now().date(),
        availability__date__lte=datetime.now().date() + timedelta(days=7)
    ).count()
    
    unread_notifications += upcoming_tours
    
    # 2. Check for recent booking confirmations (last 30 days)
    recent_confirmations = Booking.objects.filter(
        tourist=request.user,
        booking_status='confirmed',
        booking_date__gte=datetime.now() - timedelta(days=30)
    ).count()
    
    unread_notifications += min(recent_confirmations, 3)  # Cap at 3 to avoid too many notifications
    
    # 3. Add promotional notifications
    total_bookings = Booking.objects.filter(tourist=request.user).count()
    if total_bookings == 0:
        unread_notifications += 1  # Welcome/first booking discount
    elif total_bookings in [5, 10, 25]:  # Milestones
        unread_notifications += 1  # Milestone achievement notification
    
    return {
        'unread_notifications': unread_notifications,
    }
