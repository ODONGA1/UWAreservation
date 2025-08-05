# Guide and Tour Company views for ratings display
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Tour, Guide, TourCompany
from booking.models import Availability
def guide_detail(request, guide_id):
    """Detailed guide view with ratings and tours"""
    guide = get_object_or_404(Guide.objects.select_related('user'), id=guide_id)
    
    # Get availabilities led by this guide
    availabilities = Availability.objects.filter(
        guide=guide,
        date__gte=timezone.now().date()
    ).select_related('tour', 'tour__park').order_by('date')
    
    # Get tours this guide leads
    tour_ids = availabilities.values_list('tour_id', flat=True).distinct()
    tours = Tour.objects.filter(id__in=tour_ids)
    
    # Get statistics
    total_tours = tours.count()
    total_availabilities = availabilities.count()
    
    context = {
        'guide': guide,
        'availabilities': availabilities[:5],  # Show only next 5 availabilities
        'tours': tours,
        'total_tours': total_tours,
        'total_availabilities': total_availabilities,
    }
    
    return render(request, 'tours/guide_detail.html', context)


def company_detail(request, company_id):
    """Detailed tour company view with ratings and tours"""
    company = get_object_or_404(TourCompany, id=company_id)
    
    # Get company tours
    tours = Tour.objects.filter(company=company).select_related('park')
    
    # Get tour statistics
    tour_count = tours.count()
    
    # Get park count
    park_ids = tours.values_list('park_id', flat=True).distinct()
    park_count = len(park_ids)
    
    # Get operators if user has permission
    operators = []
    if request.user.is_authenticated and hasattr(request.user, 'profile') and (request.user.profile.is_staff() or company.operators.filter(id=request.user.id).exists()):
        operators = company.operators.all()
    
    context = {
        'company': company,
        'tours': tours,
        'tour_count': tour_count,
        'park_count': park_count,
        'operators': operators,
    }
    
    return render(request, 'tours/company_detail.html', context)
