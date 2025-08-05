from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Q

from .models import Rating, RatingPhoto, RatingReply, RatingHelpful
from .forms import RatingForm, RatingReplyForm


@login_required
def add_rating(request, app_label, model_name, object_id):
    """
    Generic view to add a rating for any model
    Usable with parks, tours, guides, tour companies, etc.
    """
    # Get the content type for the model being rated
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        model_class = content_type.model_class()
        obj = model_class.objects.get(id=object_id)
    except (ContentType.DoesNotExist, model_class.DoesNotExist):
        messages.error(request, "The item you're trying to rate doesn't exist.")
        return redirect('tours:tour_list')
    
    # Check if user already rated this object
    existing_rating = Rating.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=object_id
    ).first()
    
    if existing_rating:
        messages.info(request, "You've already rated this item. You can edit your rating instead.")
        return redirect('ratings:edit_rating', rating_id=existing_rating.id)
    
    # Create the rating form
    if request.method == 'POST':
        form = RatingForm(
            request.POST, 
            request.FILES,
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            instance_type=model_name
        )
        
        if form.is_valid():
            # Check if this is a verified rating (user booked the tour)
            is_verified = False
            if model_name == 'tour':
                # Check if user has a booking for this tour
                from booking.models import Booking
                bookings = Booking.objects.filter(
                    tourist=request.user,
                    availability__tour_id=object_id,
                    booking_status__in=['confirmed', 'completed']
                )
                is_verified = bookings.exists()
            
            # Save the rating
            rating = form.save(commit=False)
            rating.is_verified = is_verified
            rating.save()
            
            # Handle photos
            photos = request.FILES.getlist('photos')
            for photo in photos:
                RatingPhoto.objects.create(rating=rating, photo=photo)
            
            messages.success(request, "Thank you! Your rating has been submitted.")
            
            # Redirect to the object page
            if hasattr(obj, 'get_absolute_url'):
                return redirect(obj.get_absolute_url())
            else:
                # Default fallback
                if model_name == 'park':
                    return redirect('tours:park_detail', park_id=object_id)
                elif model_name == 'tour':
                    return redirect('tours:tour_detail', tour_id=object_id)
                else:
                    return redirect('tours:tour_list')
    else:
        # Set instance_type based on model_name
        instance_type = model_name
        
        # Initialize form
        form = RatingForm(instance_type=instance_type)
    
    # Get title based on model
    title = f"Rate this {model_name.title()}"
    if hasattr(obj, 'name'):
        object_name = obj.name
    elif hasattr(obj, 'user'):
        object_name = f"{obj.user.get_full_name() or obj.user.username}"
    else:
        object_name = str(obj)
    
    context = {
        'form': form,
        'object': obj,
        'object_name': object_name,
        'model_name': model_name,
        'title': title,
    }
    
    return render(request, 'ratings/add_rating.html', context)


@login_required
def edit_rating(request, rating_id):
    """Edit an existing rating"""
    rating = get_object_or_404(Rating, id=rating_id)
    
    # Check if user owns this rating
    if rating.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this rating")
    
    # Get the rated object
    obj = rating.content_object
    model_name = rating.content_type.model
    
    # Process the form
    if request.method == 'POST':
        form = RatingForm(
            request.POST,
            request.FILES,
            instance=rating,
            user=request.user,
            instance_type=model_name
        )
        
        if form.is_valid():
            form.save()
            
            # Handle photos
            photos = request.FILES.getlist('photos')
            for photo in photos:
                RatingPhoto.objects.create(rating=rating, photo=photo)
            
            messages.success(request, "Your rating has been updated successfully.")
            
            # Redirect to the object page
            if hasattr(obj, 'get_absolute_url'):
                return redirect(obj.get_absolute_url())
            else:
                # Default fallback
                if model_name == 'park':
                    return redirect('tours:park_detail', park_id=obj.id)
                elif model_name == 'tour':
                    return redirect('tours:tour_detail', tour_id=obj.id)
                else:
                    return redirect('tours:tour_list')
    else:
        form = RatingForm(
            instance=rating,
            instance_type=model_name
        )
    
    # Get object name for display
    if hasattr(obj, 'name'):
        object_name = obj.name
    elif hasattr(obj, 'user'):
        object_name = f"{obj.user.get_full_name() or obj.user.username}"
    else:
        object_name = str(obj)
    
    context = {
        'form': form,
        'rating': rating,
        'object': obj,
        'object_name': object_name,
        'model_name': model_name,
        'title': f"Edit Your Rating for {object_name}",
        'existing_photos': rating.photos.all(),
    }
    
    return render(request, 'ratings/edit_rating.html', context)


@login_required
@require_POST
def delete_rating_photo(request, photo_id):
    """Delete a photo from a rating"""
    photo = get_object_or_404(RatingPhoto, id=photo_id)
    rating = photo.rating
    
    # Check permissions
    if rating.user != request.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': "You don't have permission to delete this photo"})
    
    # Delete the photo
    photo.delete()
    
    return JsonResponse({
        'status': 'success',
        'message': "Photo has been deleted successfully."
    })


@login_required
@require_POST
def add_rating_reply(request, rating_id):
    """Add a reply to a rating"""
    rating = get_object_or_404(Rating, id=rating_id)
    
    # Only certain users can reply to ratings:
    # 1. Staff/admins
    # 2. Tour operators if it's their tour/company
    # 3. Guides if it's their tour/guide profile
    can_reply = False
    
    if request.user.is_staff:
        can_reply = True
    elif rating.content_type.model == 'tour':
        # Check if user is the tour's operator
        tour = rating.content_object
        if tour.company.operators.filter(id=request.user.id).exists():
            can_reply = True
    elif rating.content_type.model == 'guide':
        # Check if user is the guide
        guide = rating.content_object
        if guide.user == request.user:
            can_reply = True
    
    if not can_reply:
        return HttpResponseForbidden("You don't have permission to reply to this rating")
    
    form = RatingReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.rating = rating
        reply.user = request.user
        reply.save()
        
        messages.success(request, "Your reply has been added successfully.")
    else:
        messages.error(request, "There was an error adding your reply.")
    
    # Redirect back to the page with the rating
    obj = rating.content_object
    if hasattr(obj, 'get_absolute_url'):
        return redirect(obj.get_absolute_url())
    else:
        # Default fallback to main page
        return redirect('tours:tour_list')


@login_required
@require_POST
def mark_rating_helpful(request, rating_id):
    """Mark a rating as helpful (or toggle the status)"""
    rating = get_object_or_404(Rating, id=rating_id)
    
    # Check if user already marked this rating
    existing_vote = RatingHelpful.objects.filter(rating=rating, user=request.user).first()
    
    if existing_vote:
        # Toggle the status
        existing_vote.is_helpful = not existing_vote.is_helpful
        existing_vote.save()
        action = 'updated'
    else:
        # Create new vote
        is_helpful = request.POST.get('is_helpful', 'true').lower() == 'true'
        RatingHelpful.objects.create(
            rating=rating,
            user=request.user,
            is_helpful=is_helpful
        )
        action = 'added'
    
    # Count helpful votes
    helpful_count = rating.helpful_votes.filter(is_helpful=True).count()
    
    return JsonResponse({
        'status': 'success',
        'message': f"Your feedback has been {action} successfully.",
        'helpful_count': helpful_count
    })


def get_ratings(request, app_label, model_name, object_id):
    """Get ratings for an object - for AJAX loading"""
    # Get the content type
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    except ContentType.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'})
    
    # Get ratings
    ratings = Rating.objects.filter(
        content_type=content_type,
        object_id=object_id,
        status='approved'
    ).order_by('-is_verified', '-created_at')
    
    # Apply filters
    rating_filter = request.GET.get('filter')
    if rating_filter == 'verified':
        ratings = ratings.filter(is_verified=True)
    elif rating_filter == 'photos':
        ratings = ratings.filter(photos__isnull=False).distinct()
    elif rating_filter and rating_filter.isdigit():
        # Filter by star rating
        ratings = ratings.filter(overall_rating=int(rating_filter))
    
    # Paginate
    from django.core.paginator import Paginator
    paginator = Paginator(ratings, 5)
    page = request.GET.get('page', 1)
    ratings_page = paginator.get_page(page)
    
    # Build response
    ratings_data = []
    for rating in ratings_page:
        rating_data = {
            'id': rating.id,
            'username': rating.user.username,
            'user_full_name': rating.user.get_full_name() or rating.user.username,
            'overall_rating': rating.overall_rating,
            'comment': rating.comment,
            'created_at': rating.created_at.strftime('%b %d, %Y'),
            'is_verified': rating.is_verified,
            'helpful_count': rating.helpful_votes.filter(is_helpful=True).count(),
            'replies': [
                {
                    'username': reply.user.username,
                    'user_full_name': reply.user.get_full_name() or reply.user.username,
                    'comment': reply.comment,
                    'created_at': reply.created_at.strftime('%b %d, %Y'),
                    'is_staff': reply.user.is_staff,
                }
                for reply in rating.replies.all()
            ],
            'photos': [
                {
                    'url': photo.photo.url,
                    'caption': photo.caption,
                }
                for photo in rating.photos.all()
            ]
        }
        
        # Add specific ratings if they exist
        for field in ['value_rating', 'service_rating', 'cleanliness_rating', 'knowledge_rating']:
            value = getattr(rating, field)
            if value is not None:
                rating_data[field] = value
        
        ratings_data.append(rating_data)
    
    # Calculate rating statistics
    rating_stats = {
        'average': ratings.aggregate(avg=Avg('overall_rating'))['avg'] or 0,
        'count': ratings.count(),
        'verified_count': ratings.filter(is_verified=True).count(),
        'distribution': {
            '5': ratings.filter(overall_rating=5).count(),
            '4': ratings.filter(overall_rating=4).count(),
            '3': ratings.filter(overall_rating=3).count(),
            '2': ratings.filter(overall_rating=2).count(),
            '1': ratings.filter(overall_rating=1).count(),
        }
    }
    
    return JsonResponse({
        'status': 'success',
        'ratings': ratings_data,
        'stats': rating_stats,
        'pagination': {
            'has_next': ratings_page.has_next(),
            'has_previous': ratings_page.has_previous(),
            'current_page': ratings_page.number,
            'total_pages': paginator.num_pages,
        }
    })
