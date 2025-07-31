from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Booking, Availability
from accounts.models import Profile


class BookingForm(forms.ModelForm):
    """Form for creating new bookings"""
    
    class Meta:
        model = Booking
        fields = ['num_of_people', 'contact_email', 'contact_phone', 'special_requirements']
        widgets = {
            'num_of_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Number of people'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact email'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (optional)'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or dietary restrictions (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.availability = kwargs.pop('availability', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill contact email if user is provided
        if self.user and not self.instance.pk:
            self.fields['contact_email'].initial = self.user.email
    
    def clean_num_of_people(self):
        num_of_people = self.cleaned_data['num_of_people']
        
        if not self.availability:
            raise ValidationError("Availability information is required.")
        
        if num_of_people > self.availability.slots_available:
            raise ValidationError(
                f"Only {self.availability.slots_available} slots are available for this tour."
            )
        
        if num_of_people > self.availability.tour.max_participants:
            raise ValidationError(
                f"Maximum {self.availability.tour.max_participants} participants allowed per booking."
            )
        
        return num_of_people
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.availability and self.availability.is_past_date:
            raise ValidationError("Cannot book tours for past dates.")
        
        if self.availability and not self.availability.is_available:
            raise ValidationError("This tour is no longer available.")
        
        return cleaned_data


class AvailabilitySearchForm(forms.Form):
    """Form for searching available tours"""
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        }),
        label='From Date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='To Date'
    )
    
    park = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by park name'
        }),
        label='Park'
    )
    
    min_slots = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum available slots'
        }),
        label='Minimum Available Slots'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError("'From Date' cannot be later than 'To Date'.")
        
        if date_from and date_from < timezone.now().date():
            raise ValidationError("'From Date' cannot be in the past.")
        
        return cleaned_data


class BookingCancellationForm(forms.Form):
    """Form for booking cancellation requests"""
    
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for cancellation (optional)'
        }),
        label='Cancellation Reason'
    )
    
    confirm_cancellation = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I confirm that I want to cancel this booking'
    )


class PaymentMethodForm(forms.Form):
    """Form for selecting payment method"""
    
    PAYMENT_CHOICES = [
        ('pesapal', 'Pesapal'),
        ('dpo', 'DPO Group'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Select Payment Method'
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I agree to the terms and conditions'
    )


class AdminBookingForm(forms.ModelForm):
    """Enhanced admin form for bookings"""
    
    class Meta:
        model = Booking
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter availability to only show future dates
        if 'availability' in self.fields:
            self.fields['availability'].queryset = Availability.objects.filter(
                date__gte=timezone.now().date()
            ).select_related('tour', 'tour__park', 'guide')
    
    def clean(self):
        cleaned_data = super().clean()
        availability = cleaned_data.get('availability')
        num_of_people = cleaned_data.get('num_of_people')
        
        if availability and num_of_people:
            # Check if booking is being edited and slots need to be considered
            current_booking_people = 0
            if self.instance.pk:
                current_booking_people = self.instance.num_of_people
            
            available_slots = availability.slots_available + current_booking_people
            
            if num_of_people > available_slots:
                raise ValidationError({
                    'num_of_people': f"Only {available_slots} slots are available for this tour."
                })
        
        return cleaned_data
