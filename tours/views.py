# In tours/views.py
from django.shortcuts import render, get_object_or_404
from .models import Tour

def tour_list(request):
    """
    A view to show all tours.
    """
    tours = Tour.objects.all()
    context = {'tours': tours}
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, tour_id):
    """
    A view to show the details of a single tour.
    """
    tour = get_object_or_404(Tour, pk=tour_id)
    context = {'tour': tour}
    return render(request, 'tours/tour_detail.html', context)