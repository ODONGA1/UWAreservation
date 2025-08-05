from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.urls import reverse


class RatableMixin:
    """
    A mixin that adds rating-related functionality to a model.
    """
    def get_content_type(self):
        """Get the ContentType for this model"""
        return ContentType.objects.get_for_model(self)
        
    @property
    def average_rating(self):
        """Get the average rating for this object"""
        ratings = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        )
        if ratings.exists():
            return ratings.aggregate(avg=models.Avg('overall_rating'))['avg']
        return 0
    
    @property
    def ratings_count(self):
        """Get the number of ratings for this object"""
        return Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        ).count()
    
    def get_specific_ratings(self):
        """Get the average of each specific rating category"""
        ratings = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        )
        
        if not ratings.exists():
            return {}
        
        # Calculate average for each specific rating field
        specific_ratings = {}
        fields = [
            ('value_rating', 'Value'),
            ('service_rating', 'Service'),
            ('cleanliness_rating', 'Cleanliness'),
            ('knowledge_rating', 'Knowledge')
        ]
        
        for field, label in fields:
            avg = ratings.aggregate(avg=models.Avg(field))['avg']
            if avg:
                specific_ratings[label] = avg
        
        return specific_ratings
    
    def get_rating_breakdown(self):
        """Get the breakdown of ratings (e.g., how many 5-star, 4-star, etc.)"""
        ratings = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        )
        
        total = ratings.count()
        if total == 0:
            return []
        
        breakdown = []
        for star in range(5, 0, -1):
            count = ratings.filter(overall_rating=star).count()
            percentage = (count / total) * 100 if total > 0 else 0
            breakdown.append((star, percentage, count))
        
        return breakdown
    
    def get_add_rating_url(self):
        """Get URL to add a rating for this object"""
        content_type = ContentType.objects.get_for_model(self)
        return reverse('ratings:add_rating', kwargs={
            'app_label': content_type.app_label,
            'model_name': content_type.model,
            'object_id': self.id
        })


class Rating(models.Model):
    """
    A generic rating model that can be applied to any object in the system.
    Uses Django's ContentType framework to create a generic relation.
    """
    # The user who provided the rating
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    
    # Generic relation to the rated object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Rating values (1-5 stars)
    overall_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating (1-5 stars)"
    )
    
    # Optional specific ratings for different aspects
    value_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Value for money (1-5 stars)"
    )
    
    service_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Quality of service (1-5 stars)"
    )
    
    cleanliness_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Cleanliness (1-5 stars)"
    )
    
    knowledge_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Knowledge and information provided (1-5 stars)"
    )
    
    # Comment/review text
    comment = models.TextField(blank=True, help_text="Detailed review or feedback")
    
    # Photos (can be multiple)
    # We'll use a separate model for photos
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Rating status
    RATING_STATUS = [
        ('pending', 'Pending Moderation'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=RATING_STATUS, default='approved')
    
    # If the rating is verified (e.g., user actually booked the tour)
    is_verified = models.BooleanField(default=False, help_text="Whether this rating is from a verified booking")
    
    # Flag for staff to feature this rating (e.g., testimonials)
    is_featured = models.BooleanField(default=False, help_text="Feature this rating in testimonials or highlights")
    
    class Meta:
        ordering = ['-created_at']
        # Ensure a user can only rate an object once (can modify their rating later)
        unique_together = ('user', 'content_type', 'object_id')
    
    def __str__(self):
        return f"{self.user.username}'s {self.overall_rating}-star rating for {self.content_object}"


class RatingPhoto(models.Model):
    """Photos attached to ratings"""
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='rating_photos/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo for {self.rating}"


class RatingReply(models.Model):
    """Replies to ratings (from staff, guides, operators, etc.)"""
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Rating Replies'
    
    def __str__(self):
        return f"Reply by {self.user.username} to {self.rating}"


class RatingHelpful(models.Model):
    """Track if users find a rating helpful (like upvotes)"""
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('rating', 'user')
    
    def __str__(self):
        return f"{self.user.username} found {self.rating} {'helpful' if self.is_helpful else 'not helpful'}"
