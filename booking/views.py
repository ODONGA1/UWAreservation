from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import uuid

from .models import Availability, Booking, Payment
from .forms import BookingForm, AvailabilitySearchForm, BookingCancellationForm, PaymentMethodForm
from tours.models import Tour


def availability_list(request):
    """List available tours with search functionality"""
    form = AvailabilitySearchForm(request.GET or None)
    availabilities = Availability.objects.filter(
        date__gte=timezone.now().date(),
        slots_available__gt=0
    ).select_related('tour', 'tour__park', 'guide', 'guide__user').order_by('date')
    
    if form.is_valid():
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        park = form.cleaned_data.get('park')
        min_slots = form.cleaned_data.get('min_slots')
        
        if date_from:
            availabilities = availabilities.filter(date__gte=date_from)
        if date_to:
            availabilities = availabilities.filter(date__lte=date_to)
        if park:
            availabilities = availabilities.filter(
                Q(tour__park__name__icontains=park) | 
                Q(tour__name__icontains=park)
            )
        if min_slots:
            availabilities = availabilities.filter(slots_available__gte=min_slots)
    
    # Pagination
    paginator = Paginator(availabilities, 12)  # Show 12 tours per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'availabilities': page_obj,
    }
    return render(request, 'booking/availability_list.html', context)


def availability_detail(request, availability_id):
    """Show detailed view of a specific availability"""
    availability = get_object_or_404(
        Availability.objects.select_related('tour', 'tour__park', 'guide', 'guide__user'),
        id=availability_id
    )
    
    # Check if user can book
    can_book = availability.can_book_for(1)  # Check for at least 1 person
    
    context = {
        'availability': availability,
        'can_book': can_book,
    }
    return render(request, 'booking/availability_detail.html', context)


@login_required
def create_booking(request, availability_id):
    """Create a new booking"""
    availability = get_object_or_404(Availability, id=availability_id)
    
    if not availability.can_book_for(1):
        messages.error(request, "This tour is no longer available for booking.")
        return redirect('booking:availability_detail', availability_id=availability_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, availability=availability, user=request.user)
        if form.is_valid():
            # Check availability one more time before saving
            num_people = form.cleaned_data['num_of_people']
            if not availability.can_book_for(num_people):
                messages.error(request, "Sorry, there are not enough slots available for this booking.")
                return redirect('booking:availability_detail', availability_id=availability_id)
            
            # Create the booking
            booking = form.save(commit=False)
            booking.availability = availability
            booking.tourist = request.user
            booking.save()
            
            # Reduce available slots
            availability.slots_available -= num_people
            availability.save()
            
            messages.success(request, f"Booking created successfully! Booking ID: {booking.booking_id}")
            return redirect('booking:booking_detail', booking_id=booking.booking_id)
    else:
        form = BookingForm(availability=availability, user=request.user)
    
    context = {
        'form': form,
        'availability': availability,
    }
    return render(request, 'booking/create_booking.html', context)


@login_required
def booking_detail(request, booking_id):
    """Show booking details"""
    booking = get_object_or_404(
        Booking.objects.select_related('availability', 'availability__tour', 'availability__tour__park'),
        booking_id=booking_id,
        tourist=request.user
    )
    
    # Get or create payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total_cost,
            'payment_method': 'pending',
        }
    )
    
    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'booking/booking_detail.html', context)


@login_required
def user_bookings(request):
    """List all bookings for the current user"""
    bookings = Booking.objects.filter(
        tourist=request.user
    ).select_related(
        'availability', 'availability__tour', 'availability__tour__park'
    ).order_by('-booking_date')
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'bookings': page_obj,
    }
    return render(request, 'booking/user_bookings.html', context)


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(
        Booking.objects.select_related('availability'),
        booking_id=booking_id,
        tourist=request.user
    )
    
    if not booking.can_cancel:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('booking:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = BookingCancellationForm(request.POST)
        if form.is_valid():
            if booking.cancel_booking():
                messages.success(request, "Your booking has been cancelled successfully.")
                return redirect('booking:user_bookings')
            else:
                messages.error(request, "Unable to cancel booking. Please contact support.")
    else:
        form = BookingCancellationForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'booking/cancel_booking.html', context)


@login_required
def payment_selection(request, booking_id):
    """Select payment method for booking"""
    booking = get_object_or_404(
        Booking,
        booking_id=booking_id,
        tourist=request.user,
        booking_status='pending'
    )
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            # Get or create payment record
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_cost,
                    'payment_method': payment_method,
                }
            )
            
            if not created:
                payment.payment_method = payment_method
                payment.save()
            
            # Redirect to payment gateway or processing
            return redirect('booking:process_payment', payment_id=payment.payment_id)
    else:
        form = PaymentMethodForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'booking/payment_selection.html', context)


@login_required
def process_payment(request, payment_id):
    """Process payment (mock implementation)"""
    payment = get_object_or_404(
        Payment.objects.select_related('booking'),
        payment_id=payment_id,
        booking__tourist=request.user
    )
    
    # This is a mock implementation
    # In a real application, you would integrate with actual payment gateways
    
    if request.method == 'POST':
        # Simulate payment processing
        action = request.POST.get('action')
        
        if action == 'complete':
            # Mark payment as completed
            payment.mark_completed()
            messages.success(request, "Payment completed successfully! Your booking is confirmed.")
            return redirect('booking:booking_detail', booking_id=payment.booking.booking_id)
        
        elif action == 'fail':
            # Mark payment as failed
            payment.mark_failed("Simulated payment failure")
            messages.error(request, "Payment failed. Please try again.")
            return redirect('booking:payment_selection', booking_id=payment.booking.booking_id)
    
    context = {
        'payment': payment,
        'booking': payment.booking,
    }
    return render(request, 'booking/process_payment.html', context)


# AJAX Views for real-time availability checking

def check_availability(request):
    """AJAX endpoint to check real-time availability"""
    if request.method == 'GET':
        availability_id = request.GET.get('availability_id')
        num_people = int(request.GET.get('num_people', 1))
        
        try:
            availability = Availability.objects.get(id=availability_id)
            can_book = availability.can_book_for(num_people)
            
            return JsonResponse({
                'can_book': can_book,
                'slots_available': availability.slots_available,
                'is_past_date': availability.is_past_date,
                'message': 'Available' if can_book else 'Not available'
            })
        except Availability.DoesNotExist:
            return JsonResponse({
                'can_book': False,
                'message': 'Availability not found'
            }, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@require_POST
@csrf_exempt
def payment_webhook(request):
    """Webhook endpoint for payment gateway callbacks"""
    # This would handle callbacks from payment gateways like Pesapal or DPO
    # For now, it's a placeholder
    
    try:
        data = json.loads(request.body)
        
        # Extract payment information from webhook data
        # This structure would depend on the specific payment gateway
        gateway_transaction_id = data.get('transaction_id')
        status = data.get('status')
        
        # Find the payment record
        payment = Payment.objects.get(gateway_transaction_id=gateway_transaction_id)
        
        if status == 'completed':
            payment.mark_completed()
        elif status == 'failed':
            payment.mark_failed()
        
        return JsonResponse({'status': 'success'})
    
    except (json.JSONDecodeError, Payment.DoesNotExist, KeyError):
        return JsonResponse({'status': 'error'}, status=400)
