# In ratings/forms.py
from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import Rating, RatingPhoto, RatingReply


class RatingForm(forms.ModelForm):
    """Form for creating and editing ratings"""
    class Meta:
        model = Rating
        fields = [
            'overall_rating', 
            'value_rating', 
            'service_rating', 
            'cleanliness_rating', 
            'knowledge_rating',
            'comment'
        ]
        widgets = {
            'overall_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'value_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'service_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'cleanliness_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'knowledge_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }
    
    # We'll add custom fields for photos
    photos = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload photos from your experience (optional)'
    )
    
    def __init__(self, *args, **kwargs):
        # Allow context to be passed into the form
        self.user = kwargs.pop('user', None)
        self.content_type = kwargs.pop('content_type', None)
        self.object_id = kwargs.pop('object_id', None)
        self.instance_type = kwargs.pop('instance_type', None) # 'park', 'tour', 'guide', etc.
        
        super(RatingForm, self).__init__(*args, **kwargs)
        
        # Customize form based on what's being rated
        if self.instance_type:
            self._customize_for_instance_type()
    
    def _customize_for_instance_type(self):
        """Adjust form fields based on what's being rated"""
        if self.instance_type == 'park':
            # For parks, focus on cleanliness and value
            self.fields.pop('service_rating', None)
            self.fields.pop('knowledge_rating', None)
            self.fields['cleanliness_rating'].label = "Cleanliness & Facilities"
            self.fields['value_rating'].label = "Value for Experience"
            
        elif self.instance_type == 'guide':
            # For guides, focus on knowledge and service
            self.fields.pop('cleanliness_rating', None)
            self.fields.pop('value_rating', None)
            self.fields['knowledge_rating'].label = "Knowledge & Expertise"
            self.fields['service_rating'].label = "Communication & Helpfulness"
            
        elif self.instance_type == 'tour':
            # For tours, keep all fields
            self.fields['value_rating'].label = "Value for Money"
            self.fields['service_rating'].label = "Organization & Service"
            self.fields['cleanliness_rating'].label = "Comfort & Facilities"
            self.fields['knowledge_rating'].label = "Educational Value"
            
        elif self.instance_type == 'company':
            # For tour companies, focus on service and value
            self.fields.pop('cleanliness_rating', None)
            self.fields.pop('knowledge_rating', None)
            self.fields['service_rating'].label = "Customer Service"
            self.fields['value_rating'].label = "Value for Money"
    
    def save(self, commit=True):
        # Don't actually save yet - we need to set additional fields
        rating = super(RatingForm, self).save(commit=False)
        
        # Set the content type and object ID if provided
        if self.content_type and self.object_id:
            rating.content_type = self.content_type
            rating.object_id = self.object_id
        
        # Set the user
        if self.user and not rating.user_id:
            rating.user = self.user
            
        # If this is for a booking, mark it as verified
        # We'll implement this later when we connect to bookings
            
        # Now save
        if commit:
            rating.save()
            
            # Handle uploaded photos
            photos = self.cleaned_data.get('photos')
            if photos:
                for photo in photos:
                    RatingPhoto.objects.create(
                        rating=rating,
                        photo=photo
                    )
                    
        return rating


class RatingReplyForm(forms.ModelForm):
    """Form for replying to ratings"""
    class Meta:
        model = RatingReply
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reply to this review...'}),
        }
