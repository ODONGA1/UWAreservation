import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')
django.setup()

from ratings.models import Rating
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from tours.models import Tour, Park, Guide, TourCompany

# Check total ratings count
total_ratings = Rating.objects.count()
print(f"Total ratings: {total_ratings}")

# Check distribution by rating value
print("\nRating distribution:")
for i in range(1, 6):
    count = Rating.objects.filter(overall_rating=i).count()
    percentage = (count / total_ratings) * 100 if total_ratings > 0 else 0
    print(f"{i} stars: {count} ratings ({percentage:.1f}%)")

# Check distribution by content type
print("\nRatings by entity type:")
for model_class, name in [(Tour, "Tours"), (Park, "Parks"), (Guide, "Guides"), (TourCompany, "Tour Companies")]:
    content_type = ContentType.objects.get_for_model(model_class)
    count = Rating.objects.filter(content_type=content_type).count()
    print(f"{name}: {count} ratings")

# Show top-rated tours
print("\nTop-rated tours:")
tours = Tour.objects.all()
tour_ratings = [(tour, tour.average_rating) for tour in tours if tour.ratings_count > 0]
for tour, avg_rating in sorted(tour_ratings, key=lambda x: x[1], reverse=True)[:5]:
    print(f"{tour.name}: {avg_rating:.1f} stars ({tour.ratings_count} ratings)")
