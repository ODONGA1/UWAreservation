# In ratings/mixins.py
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Q


class RatableMixin:
    """
    A mixin for models that can be rated.
    Provides convenient methods to get ratings and calculate average scores.
    """
    @property
    def get_ratings(self):
        """Get all ratings for this object"""
        from .models import Rating
        content_type = ContentType.objects.get_for_model(self)
        return Rating.objects.filter(
            content_type=content_type, 
            object_id=self.id,
            status='approved'
        )
    
    @property
    def average_rating(self):
        """Calculate the average overall rating"""
        ratings = self.get_ratings
        if ratings.exists():
            return ratings.aggregate(Avg('overall_rating'))['overall_rating__avg']
        return 0
    
    @property
    def rating_count(self):
        """Count the number of ratings"""
        return self.get_ratings.count()
    
    def get_rating_breakdown(self):
        """Get detailed breakdown of ratings by category"""
        ratings = self.get_ratings
        if not ratings.exists():
            return {}
            
        breakdown = {
            'overall': ratings.aggregate(
                avg=Avg('overall_rating'),
                count=Count('id')
            ),
            'value': ratings.exclude(value_rating__isnull=True).aggregate(
                avg=Avg('value_rating'),
                count=Count('id', filter=Q(value_rating__isnull=False))
            ),
            'service': ratings.exclude(service_rating__isnull=True).aggregate(
                avg=Avg('service_rating'),
                count=Count('id', filter=Q(service_rating__isnull=False))
            ),
            'cleanliness': ratings.exclude(cleanliness_rating__isnull=True).aggregate(
                avg=Avg('cleanliness_rating'),
                count=Count('id', filter=Q(cleanliness_rating__isnull=False))
            ),
            'knowledge': ratings.exclude(knowledge_rating__isnull=True).aggregate(
                avg=Avg('knowledge_rating'),
                count=Count('id', filter=Q(knowledge_rating__isnull=False))
            )
        }
        
        return breakdown
    
    def get_recent_ratings(self, limit=5):
        """Get the most recent ratings"""
        return self.get_ratings.order_by('-created_at')[:limit]
    
    def get_featured_ratings(self, limit=3):
        """Get featured ratings (testimonials)"""
        return self.get_ratings.filter(is_featured=True).order_by('-created_at')[:limit]
