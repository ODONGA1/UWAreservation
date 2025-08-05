from django import template
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from ratings.models import Rating

register = template.Library()

@register.filter
def star_size_class(size):
    """
    Convert size string to Tailwind CSS classes for star icons
    """
    if size == "sm":
        return "w-4 h-4"
    elif size == "lg":
        return "w-8 h-8"
    else:  # md or default
        return "w-6 h-6"
        
@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def display_star_rating(value, max_value=5, size='md'):
    """
    Display star rating with Font Awesome icons
    Usage: {% display_star_rating tour.average_rating %}
    """
    if value is None:
        value = 0
        
    whole_stars = int(value)
    decimal_part = value - whole_stars
    half_star = decimal_part >= 0.25 and decimal_part < 0.75
    full_stars_after_half = 5 - whole_stars - (1 if half_star else 0)
    
    # Determine classes based on size
    if size == 'sm':
        size_class = 'fa-sm'
    elif size == 'lg':
        size_class = 'fa-lg'
    else:
        size_class = ''
    
    result = []
    # Full stars
    for _ in range(whole_stars):
        result.append(f'<i class="fas fa-star text-yellow-400 {size_class}"></i>')
    
    # Half star if applicable
    if half_star:
        result.append(f'<i class="fas fa-star-half-alt text-yellow-400 {size_class}"></i>')
    
    # Empty stars
    if decimal_part >= 0.75:
        stars_to_add = max_value - whole_stars - 1
    else:
        stars_to_add = max_value - whole_stars - (1 if half_star else 0)
    
    for _ in range(stars_to_add):
        result.append(f'<i class="far fa-star text-yellow-400 {size_class}"></i>')
    
    return mark_safe(''.join(result))

@register.simple_tag
def display_rating_summary(obj):
    """
    Display a summary of ratings including average and count
    Usage: {% display_rating_summary tour %}
    """
    if not hasattr(obj, 'average_rating') or not hasattr(obj, 'ratings_count'):
        return mark_safe('<span class="text-gray-500">No ratings yet</span>')
    
    avg = obj.average_rating
    count = obj.ratings_count
    
    if avg == 0 or count == 0:
        return mark_safe('<span class="text-gray-500">No ratings yet</span>')
    
    stars = display_star_rating(avg, size='sm')
    return mark_safe(f'{stars} <span class="ml-1 text-gray-600">({avg:.1f}) · {count} {"reviews" if count != 1 else "review"}</span>')

@register.inclusion_tag('ratings/includes/rating_breakdown.html')
def show_rating_breakdown(obj):
    """
    Display a detailed breakdown of ratings
    Usage: {% show_rating_breakdown tour %}
    """
    if not hasattr(obj, 'get_rating_breakdown'):
        return {'breakdown': [], 'ratings_count': 0}
        
    breakdown = obj.get_rating_breakdown()
    return {
        'breakdown': breakdown,
        'ratings_count': obj.ratings_count
    }

@register.inclusion_tag('ratings/includes/recent_ratings.html')
def show_recent_ratings(obj, limit=3):
    """
    Display recent ratings for an object
    Usage: {% show_recent_ratings tour %}
    """
    if not hasattr(obj, 'get_content_type'):
        return {'ratings': []}
    
    content_type = obj.get_content_type()
    ratings = Rating.objects.filter(
        content_type=content_type,
        object_id=obj.id,
        status='approved'
    ).select_related('user').order_by('-created_at')[:limit]
    
    return {
        'ratings': ratings,
        'obj': obj
    }

@register.inclusion_tag('ratings/includes/specific_ratings.html')
def show_specific_ratings(obj):
    """
    Display specific category ratings (like cleanliness, value, etc.)
    Usage: {% show_specific_ratings tour %}
    """
    if not hasattr(obj, 'get_specific_ratings'):
        return {'specific_ratings': {}}
    
    return {
        'specific_ratings': obj.get_specific_ratings()
    }

@register.inclusion_tag('ratings/includes/rating_button.html')
def show_rating_button(obj, user):
    """
    Display button to add or edit rating
    Usage: {% show_rating_button tour user %}
    """
    can_rate = user.is_authenticated
    has_rated = False
    rating_url = "#"
    
    if hasattr(obj, 'get_add_rating_url') and can_rate:
        rating_url = obj.get_add_rating_url()
        
        # Check if user has already rated this object
        if hasattr(obj, 'get_content_type'):
            content_type = obj.get_content_type()
            has_rated = Rating.objects.filter(
                content_type=content_type,
                object_id=obj.id,
                user=user
            ).exists()
    
    return {
        'obj': obj,
        'can_rate': can_rate,
        'has_rated': has_rated,
        'rating_url': rating_url
    }
