from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Park, Tour, Guide
from booking.models import Availability


class ParkForm(forms.ModelForm):
    """Form for creating and editing parks"""
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter park name'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Describe the park, its features, wildlife, and attractions...',
            'rows': 6
        })
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Park location (e.g., Northern Uganda, Western Uganda)'
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-safari-50 file:text-safari-700 hover:file:bg-safari-100',
            'accept': 'image/*'
        }),
        help_text="Upload a beautiful image of the park (optional)"
    )
    
    # Additional detailed fields
    park_type = forms.ChoiceField(
        choices=[
            ('national_park', 'National Park'),
            ('wildlife_reserve', 'Wildlife Reserve'),
            ('sanctuary', 'Wildlife Sanctuary'),
            ('forest_reserve', 'Forest Reserve'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
        })
    )
    
    date_established = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'type': 'date'
        }),
        help_text="Date when the park was established"
    )
    
    area_sqkm = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Area in square kilometers',
            'step': '0.01'
        })
    )
    
    altitude_m = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Altitude in meters above sea level'
        })
    )
    
    latitude = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Latitude (decimal degrees)',
            'step': '0.000001'
        })
    )
    
    longitude = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Longitude (decimal degrees)',
            'step': '0.000001'
        })
    )
    
    vegetation_type = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Describe the vegetation types and plant species...',
            'rows': 4
        })
    )
    
    key_wildlife = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'List key wildlife species found in the park...',
            'rows': 4
        })
    )
    
    key_features = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Describe key physical features and attractions...',
            'rows': 4
        })
    )
    
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Contact email for the park'
        })
    )
    
    contact_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Contact phone number'
        })
    )
    
    website_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Official website URL'
        })
    )

    class Meta:
        model = Park
        fields = ('name', 'description', 'location', 'image', 'park_type', 'date_established', 
                 'area_sqkm', 'altitude_m', 'latitude', 'longitude', 'vegetation_type', 
                 'key_wildlife', 'key_features', 'contact_email', 'contact_phone', 'website_url')

    def clean_name(self):
        name = self.cleaned_data['name']
        # Check if park name already exists (excluding current instance for editing)
        if Park.objects.filter(name__iexact=name).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("A park with this name already exists.")
        return name


class TourForm(forms.ModelForm):
    """Form for creating and editing tours"""
    park = forms.ModelChoiceField(
        queryset=Park.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
        }),
        empty_label="Select a park"
    )
    company = forms.ModelChoiceField(
        queryset=None,  # We'll set this in __init__
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
        }),
        empty_label="Select a tour company"
    )
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter tour name'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Describe the tour, what visitors will see and do...',
            'rows': 5
        })
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        })
    )
    duration_hours = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Hours',
            'min': '1',
            'max': '168'  # 1 week max
        }),
        help_text="Duration in hours (1-168)"
    )
    max_participants = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Maximum number of participants',
            'min': '1',
            'max': '100'
        }),
        help_text="Maximum number of participants per tour"
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-safari-50 file:text-safari-700 hover:file:bg-safari-100',
            'accept': 'image/jpeg,image/jpg,image/png,image/webp',
            'id': 'tour-image-upload'
        }),
        help_text="Upload an image for the tour (JPEG, JPG, PNG, WebP - Max 20MB)"
    )

    class Meta:
        model = Tour
        fields = ('park', 'company', 'name', 'description', 'price', 'duration_hours', 'max_participants', 'image')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        from .models import TourCompany
        from django.db.models import Q
        
        # Get the current tour's company if this is an edit form
        current_company = None
        if self.instance and self.instance.pk:
            current_company = self.instance.company
        
        # Handle company field based on user permissions
        if self.user and hasattr(self.user, 'profile'):
            profile = self.user.profile
            
            # Superuser can choose any company
            if self.user.is_superuser:
                self.fields['company'].queryset = TourCompany.objects.all()
            
            # Users with both operator and staff roles
            elif profile.is_operator() and profile.is_staff():
                # Can choose from their companies and UWA
                base_queryset = TourCompany.objects.filter(
                    Q(operators=self.user) | 
                    Q(is_uwa=True)
                ).distinct()
                
                # Include current company if editing and not already in queryset
                if current_company and not base_queryset.filter(id=current_company.id).exists():
                    self.fields['company'].queryset = TourCompany.objects.filter(
                        Q(operators=self.user) | 
                        Q(is_uwa=True) |
                        Q(id=current_company.id)
                    ).distinct()
                else:
                    self.fields['company'].queryset = base_queryset
            
            # Regular UWA staff can only choose UWA company
            elif profile.is_staff():
                base_queryset = TourCompany.objects.filter(is_uwa=True)
                
                # Include current company if editing and not already in queryset
                if current_company and not base_queryset.filter(id=current_company.id).exists():
                    self.fields['company'].queryset = TourCompany.objects.filter(
                        Q(is_uwa=True) |
                        Q(id=current_company.id)
                    ).distinct()
                else:
                    self.fields['company'].queryset = base_queryset
                
                # Pre-select UWA company if it exists and this is a new tour
                if not self.instance.pk and self.fields['company'].queryset.count() == 1:
                    self.fields['company'].initial = self.fields['company'].queryset.first()
            
            # Tour operators can only choose their own companies
            elif profile.is_operator():
                base_queryset = TourCompany.objects.filter(operators=self.user)
                
                # Include current company if editing and not already in queryset
                if current_company and not base_queryset.filter(id=current_company.id).exists():
                    self.fields['company'].queryset = TourCompany.objects.filter(
                        Q(operators=self.user) |
                        Q(id=current_company.id)
                    ).distinct()
                else:
                    self.fields['company'].queryset = base_queryset
                
                # If operator has only one company, pre-select it for new tours
                if not self.instance.pk and self.fields['company'].queryset.count() == 1:
                    self.fields['company'].initial = self.fields['company'].queryset.first()
            else:
                # Default, show all companies but with warning
                self.fields['company'].queryset = TourCompany.objects.all()
        else:
            # Default, show all companies
            self.fields['company'].queryset = TourCompany.objects.all()
        
        # Ensure the current company is set as initial for edit forms
        if current_company:
            self.fields['company'].initial = current_company

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price

    def clean_duration_hours(self):
        duration = self.cleaned_data['duration_hours']
        if duration < 1 or duration > 168:
            raise forms.ValidationError("Duration must be between 1 and 168 hours.")
        return duration

    def clean_max_participants(self):
        max_participants = self.cleaned_data['max_participants']
        if max_participants < 1:
            raise forms.ValidationError("Maximum participants must be at least 1.")
        return max_participants
        
    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company:
            return company
            
        # Skip validation if no user is set
        if not self.user or not hasattr(self.user, 'profile'):
            return company
            
        profile = self.user.profile
        
        # Superusers can choose any company
        if self.user.is_superuser:
            return company
            
        # Users with both operator and staff roles
        if profile.is_operator() and profile.is_staff():
            # Can choose from their companies and UWA
            if company.is_uwa or company.operators.filter(id=self.user.id).exists():
                return company
            raise forms.ValidationError("You can only select your own company or UWA.")
            
        # Regular UWA staff can only choose UWA company
        if profile.is_staff():
            if company.is_uwa:
                return company
            raise forms.ValidationError("As UWA staff, you can only create UWA tours.")
            
        # Tour operators can only choose their own companies
        if profile.is_operator():
            if company.operators.filter(id=self.user.id).exists():
                return company
            raise forms.ValidationError("You can only select your own company.")
            
        return company

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (20MB limit)
            if image.size > 20 * 1024 * 1024:  # 20MB in bytes
                raise forms.ValidationError("Image file too large. Please select an image smaller than 20MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if hasattr(image, 'content_type'):
                if image.content_type not in allowed_types:
                    raise forms.ValidationError("Invalid file type. Please upload a JPEG, JPG, PNG, or WebP image.")
            
            # Check file extension as backup
            if hasattr(image, 'name'):
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                if not any(image.name.lower().endswith(ext) for ext in allowed_extensions):
                    raise forms.ValidationError("Invalid file extension. Please upload a JPEG, JPG, PNG, or WebP image.")
        
        return image


class AvailabilityForm(forms.ModelForm):
    """Form for creating and managing tour availabilities/dates"""
    
    # Allow selecting from operator's tours or all tours for staff
    tour = forms.ModelChoiceField(
        queryset=Tour.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'id': 'tour-select'
        }),
        empty_label="Select a tour"
    )
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        }),
        help_text="Select the date for this tour availability"
    )
    
    total_slots = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Total available slots',
            'min': '1',
            'max': '100'
        }),
        help_text="Total number of slots available for booking"
    )
    
    reserved_slots = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Reserved slots (optional)',
            'min': '0'
        }),
        help_text="Number of slots to reserve for offline bookings or VIP guests"
    )
    
    guide = forms.ModelChoiceField(
        queryset=Guide.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
        }),
        empty_label="No guide assigned",
        help_text="Assign a guide to this tour date (optional)"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Special notes for this tour date...',
            'rows': 3
        }),
        help_text="Special notes for this tour date (optional)"
    )

    class Meta:
        model = Availability
        fields = ('tour', 'date', 'guide')
        exclude = ('slots_available',)  # We'll set this in the save method

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Customize the guide dropdown to show names
        guide_choices = [('', 'No guide assigned')]
        for guide in Guide.objects.select_related('user').all():
            name = f"{guide.user.first_name} {guide.user.last_name}".strip()
            if guide.specialization:
                name += f" ({guide.specialization})"
            guide_choices.append((guide.id, name or guide.user.username))
        
        self.fields['guide'].choices = guide_choices
        
        # Restrict tour choices based on user's role and company
        if self.user:
            from django.db.models import Q
            
            if self.user.is_superuser:
                # Superuser can see all tours
                pass
            elif hasattr(self.user, 'profile'):
                profile = self.user.profile
                
                if profile.is_operator() and profile.is_staff():
                    # User with both operator and staff roles can see their company tours and UWA tours
                    self.fields['tour'].queryset = Tour.objects.filter(
                        Q(company__operators=self.user) | 
                        Q(company__is_uwa=True)
                    ).order_by('name')
                elif profile.is_operator():
                    # Regular operators only see their company's tours
                    self.fields['tour'].queryset = Tour.objects.filter(
                        company__operators=self.user
                    ).order_by('name')
                elif profile.is_staff():
                    # UWA staff only see UWA tours
                    self.fields['tour'].queryset = Tour.objects.filter(
                        company__is_uwa=True
                    ).order_by('name')
                else:
                    # Regular users don't see any tours
                    self.fields['tour'].queryset = Tour.objects.none()
        
        # If we're editing an existing instance, set initial values
        if self.instance.pk:
            self.fields['total_slots'].initial = self.instance.slots_available
            if hasattr(self.instance, 'reserved_slots'):
                self.fields['reserved_slots'].initial = self.instance.reserved_slots
            
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        tour = cleaned_data.get('tour')
        total_slots = cleaned_data.get('total_slots')
        reserved_slots = cleaned_data.get('reserved_slots', 0) or 0  # Default to 0 if None
        
        # Date validation
        if date and date < timezone.now().date():
            raise ValidationError({'date': "Tour date cannot be in the past."})
        
        # Check if tour and date combination already exists (for new entries)
        if tour and date and not self.instance.pk:
            if Availability.objects.filter(tour=tour, date=date).exists():
                raise ValidationError("This tour already has availability set for this date.")
        
        # Slots validation
        if total_slots and total_slots < 1:
            raise ValidationError({'total_slots': "Total slots must be at least 1."})
            
        if reserved_slots and reserved_slots < 0:
            raise ValidationError({'reserved_slots': "Reserved slots cannot be negative."})
            
        if total_slots and reserved_slots and reserved_slots > total_slots:
            raise ValidationError({'reserved_slots': "Reserved slots cannot exceed total slots."})
            
        # Check against tour's maximum participants
        if tour and total_slots and total_slots > tour.max_participants:
            raise ValidationError({
                'total_slots': f"Total slots cannot exceed the tour's maximum participants ({tour.max_participants})."
            })
            
        return cleaned_data
        
    def clean_tour(self):
        tour = self.cleaned_data.get('tour')
        
        if not tour or not self.user:
            return tour
            
        if self.user.is_superuser:
            return tour
            
        if hasattr(self.user, 'profile'):
            profile = self.user.profile
            
            # Users with both operator and staff roles
            if profile.is_operator() and profile.is_staff():
                # Can choose from their companies and UWA
                if tour.company.is_uwa or tour.company.operators.filter(id=self.user.id).exists():
                    return tour
                raise forms.ValidationError("You can only select tours from your own company or UWA.")
                
            # Regular UWA staff can only choose UWA tours
            if profile.is_staff():
                if tour.company.is_uwa:
                    return tour
                raise forms.ValidationError("As UWA staff, you can only select UWA tours.")
                
            # Tour operators can only choose their own companies' tours
            if profile.is_operator():
                if tour.company.operators.filter(id=self.user.id).exists():
                    return tour
                raise forms.ValidationError("You can only select tours from your own company.")
                
        return tour
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calculate available slots (total minus reserved)
        total_slots = self.cleaned_data.get('total_slots', 0)
        reserved_slots = self.cleaned_data.get('reserved_slots', 0) or 0
        
        # Set the slots_available field
        instance.slots_available = total_slots - reserved_slots
        
        # We'll ignore reserved_slots and notes fields if the model doesn't have them
        # This way the form still works without these fields in the model
        
        if commit:
            instance.save()
            
        return instance  # Important: return the instance
            
        return instance
            
        return instance
