import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth import get_user_model
from tours.models import Tour, Park, Guide, TourCompany
from ratings.models import Rating, RatingPhoto, RatingReply, RatingHelpful

User = get_user_model()

# Sample rating titles for different rating levels
RATING_TITLES = {
    5: [
        "Absolutely phenomenal experience!", 
        "Best tour of my life!", 
        "Worth every penny and more!",
        "Breathtaking adventure!",
        "Exceeded all expectations!",
        "A perfect day in nature!",
        "Unforgettable wildlife encounter!",
        "Amazing from start to finish!"
    ],
    4: [
        "Great experience overall", 
        "Very enjoyable tour", 
        "Definitely recommend this tour",
        "Wonderful wildlife sightings",
        "Really good value for money",
        "Professional and knowledgeable guides",
        "Beautiful scenery and good service"
    ],
    3: [
        "Decent tour with some minor issues", 
        "Average experience", 
        "Good but could be better",
        "Some nice moments but a few disappointments",
        "Not bad, not great",
        "Satisfactory overall"
    ],
    2: [
        "Disappointing experience", 
        "Not worth the price", 
        "Several issues need addressing",
        "Underwhelming tour",
        "Poor organization",
        "Expected much more"
    ],
    1: [
        "Terrible experience", 
        "Complete waste of money", 
        "Avoid this tour at all costs!",
        "Extremely disappointing",
        "So many problems",
        "Worst tour experience ever"
    ]
}

# Sample comments for different types of tours and rating levels
TOUR_COMMENTS = {
    5: [
        "The wildlife sightings were incredible! We saw so many animals up close. Our guide was extremely knowledgeable and made sure we had the best experience possible. The vehicle was comfortable and the whole day was perfectly organized.",
        "What an amazing adventure! Our guide knew exactly where to find the animals. We saw elephants, lions, giraffes, and so much more. The lunch provided was delicious, and the views were breathtaking. Will definitely come back!",
        "This tour exceeded all our expectations. The guides were professional, friendly, and incredibly knowledgeable about the local wildlife and ecosystem. They answered all our questions and made sure everyone in the group had a great time.",
        "Absolutely worth every penny! The tour was well-paced, allowing enough time to enjoy each sighting. Our guide's passion for wildlife conservation was inspiring. The park is stunning and we got amazing photos."
    ],
    4: [
        "Really enjoyed this tour. Our guide was knowledgeable and we saw plenty of wildlife. The only minor issue was that the vehicle was a bit crowded. Otherwise, a great experience that I would recommend.",
        "Beautiful park and excellent guide. We saw most of the animals we hoped to see. The lunch provided was good quality. Just wish we had a bit more time at certain viewing spots.",
        "Very good experience overall. The guide was friendly and informative. Weather wasn't perfect but that's obviously not the tour company's fault. Would recommend bringing extra water and sunscreen.",
        "Great day out in nature. The tour was well organized and our guide was excellent. Only giving 4 stars because the drive was quite long and bumpy, but I understand that's part of the safari experience."
    ],
    3: [
        "Mixed experience. While the park itself is beautiful and we did see some animals, our guide wasn't very communicative and seemed rushed. Lunch was basic but adequate.",
        "An okay tour. The wildlife was nice when we spotted them, but we spent a lot of time driving around without seeing much. The guide was knowledgeable but not very engaging.",
        "Average experience. The tour delivered what was promised, but nothing exceptional. There were too many people in our group which made it difficult to hear the guide at times.",
        "The park was beautiful but the tour itself was somewhat disorganized. We started late and felt rushed through some areas. The guide knew about the animals but wasn't very enthusiastic."
    ],
    2: [
        "Disappointed with this tour. We hardly saw any wildlife, and the guide didn't seem to make much effort to track animals. The vehicle was uncomfortable and the lunch provided was very basic.",
        "Not a good value for money. The tour description promised much more than what we experienced. The guide seemed inexperienced and couldn't answer many of our questions.",
        "Several issues with this tour. We started over an hour late, the vehicle had mechanical problems, and the guide was not very knowledgeable. The only saving grace was the natural beauty of the park.",
        "Expected much more based on the description and price. The tour was rushed, the group size was too large, and we missed seeing many of the animals mentioned in the tour description."
    ],
    1: [
        "Terrible experience from start to finish. The tour started late, the vehicle broke down, we barely saw any wildlife, and the guide was unprofessional. Complete waste of money.",
        "Worst tour I've ever been on. Nothing went as described. The guide barely spoke English, we didn't see most of the promised wildlife, and the lunch provided was inedible. Avoid at all costs!",
        "Extremely disappointing. The tour operator seems to care only about taking your money. The 'comfortable vehicle' was an old van with broken seats, and the 'experienced guide' knew less than I did after reading a guidebook.",
        "I regret booking this tour. It was disorganized, unprofessional, and not at all what was advertised. The only wildlife we saw were some birds and one distant antelope. Save your money and go elsewhere."
    ]
}

# Sample comments specific to gorilla trekking
GORILLA_COMMENTS = {
    5: [
        "The gorilla encounter was life-changing! After a challenging trek through the forest, seeing these magnificent creatures up close was breathtaking. Our guide was exceptional in tracking the gorillas and ensuring we had a safe, respectful encounter.",
        "Words can't describe the feeling of sitting just meters away from a family of mountain gorillas. The trek was difficult but absolutely worth it. The guides were experts at finding the gorillas and shared fascinating information about their behavior.",
        "This gorilla trekking experience exceeded all expectations. The preparation briefing was thorough, the guides were professional, and the gorilla family we visited was amazing to observe. The hour spent with them went by too quickly!",
        "An unforgettable wildlife encounter! The trek through the forest was challenging but well-managed by our experienced guides. The moment we first spotted the gorillas was magical. Truly a bucket list experience worth every penny and effort."
    ],
    4: [
        "Amazing gorilla encounter! The trek was more strenuous than expected (be prepared for rough terrain), but seeing the gorillas was incredible. Our guide was knowledgeable but sometimes hard to understand.",
        "Great experience tracking gorillas. The family we visited had several youngsters playing which was delightful to watch. Only giving 4 stars because the briefing before the trek was rushed and could have been more informative.",
        "Wonderful wildlife experience. The gorillas were magnificent and we got quite close. The trek was challenging in the rain though, and some better preparation tips would have been helpful.",
        "Really good gorilla trekking experience. The guides were excellent at tracking. Just be aware that the trek can be very demanding physically - more warning about this would have been appreciated."
    ],
    3: [
        "Mixed experience. The gorilla sighting was amazing of course, but brief as they were moving through the forest. The trek was extremely difficult and I don't think the tour description adequately prepared us for the physical demands.",
        "Seeing the gorillas was incredible, but the organization was lacking. We waited for hours before starting the trek with minimal communication from staff. The actual encounter was shorter than the promised one hour.",
        "An okay experience. The gorillas were impressive but we were kept quite far from them compared to other groups. The hike was very strenuous and the pace was too fast for some in our group.",
        "The gorilla encounter itself deserves 5 stars, but the overall experience was just average. Poor communication, disorganized starting process, and inadequate briefing about what to expect."
    ],
    2: [
        "Disappointed with several aspects of this tour. The gorilla sighting was very brief (about 15 minutes) before they moved away, despite paying for a full hour. The guides rushed us through the experience and were not very informative.",
        "Not worth the high price. The trek was extremely difficult (much more than described) and when we finally reached the gorillas, we could barely see them through thick vegetation. The guides seemed impatient with questions.",
        "The gorilla sighting was okay but too brief and distant. The main issues were with the tour organization - confusing instructions, last-minute changes to the meeting point, and inadequate equipment recommendations.",
        "Expected much more based on the description and enormous cost. The trek was poorly managed, our group was too large, and the time with the gorillas was cut short because we started late."
    ],
    1: [
        "Terrible experience. After an exhausting 5-hour trek through mud and rain, we only glimpsed the gorillas from a distance for about 10 minutes before the guide rushed us away. Complete waste of money and time.",
        "Avoid this gorilla trek! Extremely unprofessional guides who were more interested in chatting among themselves than providing information. The briefing was inadequate, and the actual gorilla encounter was disappointing and brief.",
        "One of the worst wildlife experiences I've had. The trek was dangerous with inadequate safety measures, the guides were unhelpful, and we barely saw the gorillas through thick foliage for a few minutes.",
        "I regret booking this tour. Nothing went as described. The 'moderate' trek was extremely difficult and dangerous, the guides were unprepared, and the gorilla sighting was so brief and distant it was hardly worth the effort."
    ]
}

# Sample comments specific to boat safaris
BOAT_COMMENTS = {
    5: [
        "The boat safari was incredible! We saw hippos, crocodiles, and countless bird species up close. Our guide was extremely knowledgeable about the local ecosystem and wildlife behavior. The boat was comfortable and the views were spectacular.",
        "Amazing water safari experience! Getting so close to hippos safely was thrilling. The captain was skilled and knew exactly where to find wildlife. The perspective from the water offers a unique way to see the park's animals.",
        "This boat tour exceeded all expectations. The guides spotted wildlife that we would have never seen ourselves. We saw elephants coming to drink at the shore, hippos, crocodiles, and beautiful water birds. A photographer's dream!",
        "Absolutely fantastic boat safari! The early morning start was worth it as we saw animals coming to the water's edge at sunrise. The boat was stable and comfortable, and the guide's commentary was informative and entertaining."
    ],
    4: [
        "Really enjoyable boat safari. We saw plenty of hippos, some crocodiles, and beautiful birds. The guide was knowledgeable and friendly. Would have given 5 stars but the boat was quite crowded which limited viewing angles at times.",
        "Great experience on the water. The wildlife sightings were excellent - especially the hippos and elephants at the shore. The only drawback was that the life jackets were old and not very comfortable.",
        "Very good boat tour. We saw amazing wildlife including hippo families and a huge crocodile. The guide was informative. Just one star off because the tour started late and felt slightly rushed toward the end.",
        "Excellent way to see wildlife from a different perspective. The boat captain was skilled and got us close to the animals safely. Good commentary from the guide. Only recommendation would be to provide sun canopies on all boats."
    ],
    3: [
        "Decent boat safari but a bit underwhelming. We saw some hippos and birds but not as much wildlife as expected. The boat was comfortable and the guide was friendly, though not particularly informative about the animals.",
        "An okay experience. The scenery was beautiful and we did see hippos, but they were quite distant. The boat engine was quite loud which may have scared away some wildlife. The guide tried his best but seemed inexperienced.",
        "Mixed experience on the boat safari. Some nice wildlife sightings but long periods of seeing nothing. The boat was overcrowded which made it difficult to take photos. The sunset on the water was beautiful though.",
        "Average boat tour. We saw the standard hippos and a few crocodiles, but the guide didn't make much effort to find other wildlife. The boat was functional but not particularly comfortable for a three-hour tour."
    ],
    2: [
        "Disappointed with this boat safari. The boat was overcrowded and unstable. We barely saw any wildlife except for a few distant hippos. The guide provided very little information and seemed uninterested.",
        "Not a good experience. The boat had mechanical problems and we had to return early. Before that, the wildlife sightings were minimal and the guide couldn't answer basic questions about the animals we did see.",
        "Several issues with this boat tour. It started over an hour late, the life jackets were worn and dirty, and the guide was constantly on his phone instead of spotting wildlife or providing information.",
        "Expected much more based on the description. The boat was uncomfortable with hard seats, the engine was very loud, and we saw very few animals. Not worth the price charged."
    ],
    1: [
        "Terrible boat safari experience. The boat seemed unsafe, the guide knew almost nothing about wildlife, and we spent most of the time stuck in one spot due to engine problems. Complete waste of time and money.",
        "Worst boat tour ever. The captain was reckless, getting dangerously close to hippos which clearly agitated them. The guide provided incorrect information about the wildlife, and the boat was dirty and uncomfortable.",
        "Extremely disappointing boat safari. We saw almost no wildlife despite the brochure promising abundant sightings. The boat was overcrowded with twice as many people as seats, and the guide was unprofessional.",
        "I regret booking this boat tour. It was dangerous, disorganized, and not at all what was advertised. The boat leaked water, had no safety equipment, and the guide spent more time chatting with the captain than pointing out wildlife."
    ]
}

class Command(BaseCommand):
    help = 'Generates dummy ratings for tours, parks, guides, and tour companies'

    def add_arguments(self, parser):
        parser.add_argument('--tours', type=int, default=20, help='Number of ratings per tour')
        parser.add_argument('--parks', type=int, default=10, help='Number of ratings per park')
        parser.add_argument('--guides', type=int, default=5, help='Number of ratings per guide')
        parser.add_argument('--companies', type=int, default=8, help='Number of ratings per company')
        parser.add_argument('--reset', action='store_true', help='Delete existing ratings before creating new ones')
        
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Deleting existing ratings...')
            Rating.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All ratings deleted.'))
        
        # Get all users who aren't staff (potential customers)
        customers = User.objects.filter(is_staff=False)
        if not customers.exists():
            self.stdout.write(self.style.ERROR('No customer users found. Please create some users first.'))
            return
            
        # Get staff users for replies
        staff_users = User.objects.filter(is_staff=True)
        if not staff_users.exists():
            self.stdout.write(self.style.WARNING('No staff users found. No replies will be created.'))
            
        # Generate ratings for tours
        self.generate_ratings_for_model(
            Tour, 
            options['tours'],
            customers,
            staff_users,
            comment_source='tour'
        )
        
        # Generate ratings for parks
        self.generate_ratings_for_model(
            Park, 
            options['parks'],
            customers,
            staff_users,
            comment_source='park'
        )
        
        # Generate ratings for guides
        self.generate_ratings_for_model(
            Guide, 
            options['guides'],
            customers,
            staff_users,
            comment_source='guide'
        )
        
        # Generate ratings for tour companies
        self.generate_ratings_for_model(
            TourCompany, 
            options['companies'],
            customers,
            staff_users,
            comment_source='company'
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully generated dummy ratings!'))
    
    def generate_ratings_for_model(self, model_class, count_per_object, customers, staff_users, comment_source):
        """Generate ratings for all objects of the given model class"""
        content_type = ContentType.objects.get_for_model(model_class)
        model_name = model_class.__name__
        
        objects = model_class.objects.all()
        if not objects.exists():
            self.stdout.write(f'No {model_name} objects found to rate.')
            return
            
        self.stdout.write(f'Generating ratings for {model_name}...')
        
        for obj in objects:
            try:
                name = obj.name
            except AttributeError:
                if hasattr(obj, 'user'):
                    name = obj.user.get_full_name() or obj.user.username
                else:
                    name = f"{model_name} #{obj.id}"
                
            self.stdout.write(f'  Creating ratings for {name}')
            
            # Determine the average rating tendency for this object (between 3.5 and 4.8)
            # This makes some tours/guides/etc. consistently better rated than others
            rating_tendency = round(random.uniform(3.5, 4.8), 1)
            
            # First get a list of customers who haven't rated this object yet
            available_customers = list(customers)
            existing_ratings = Rating.objects.filter(
                content_type=content_type,
                object_id=obj.id
            ).values_list('user_id', flat=True)
            
            # Remove customers who have already rated this object
            for user_id in existing_ratings:
                available_customers = [c for c in available_customers if c.id != user_id]
            
            # If we don't have enough customers for all ratings, just use the available ones
            actual_count = min(count_per_object, len(available_customers))
            
            if actual_count == 0:
                self.stdout.write(f'  No available customers to rate {name}')
                continue
                
            self.stdout.write(f'  Creating {actual_count} ratings for {name}')
            
            # Use random.sample to get unique customers for each rating
            selected_customers = random.sample(available_customers, actual_count)
            
            for customer in selected_customers:
                # Create rating with some randomness but influenced by the tendency
                rating_value = self.get_weighted_rating(rating_tendency)
                
                # Determine when the rating was left (between 1 and 180 days ago)
                days_ago = random.randint(1, 180)
                created_date = timezone.now() - timedelta(days=days_ago)
                
                # Generate specific ratings based on object type
                specific_ratings = self.generate_specific_ratings(model_class, rating_value)
                
                # Get appropriate comment and title based on the rating
                if 'Gorilla' in getattr(obj, 'name', '') and comment_source == 'tour':
                    comment = random.choice(GORILLA_COMMENTS.get(rating_value, GORILLA_COMMENTS[3]))
                elif 'Boat' in getattr(obj, 'name', '') and comment_source == 'tour':
                    comment = random.choice(BOAT_COMMENTS.get(rating_value, BOAT_COMMENTS[3]))
                else:
                    comment = random.choice(TOUR_COMMENTS.get(rating_value, TOUR_COMMENTS[3]))
                
                # Create the rating
                rating = Rating.objects.create(
                    content_type=content_type,
                    object_id=obj.id,
                    user=customer,
                    overall_rating=rating_value,
                    value_rating=specific_ratings.get('value_rating'),
                    service_rating=specific_ratings.get('service_rating'),
                    cleanliness_rating=specific_ratings.get('cleanliness_rating'),
                    knowledge_rating=specific_ratings.get('knowledge_rating'),
                    comment=comment,
                    is_verified=random.choice([True, True, False]),  # 2/3 chance of being verified
                )
                
                # Set creation date (needs to be done after creation to bypass auto_now_add)
                rating.created_at = created_date
                rating.save(update_fields=['created_at'])
                
                # Randomly add replies to some ratings
                if staff_users and random.random() < 0.3:  # 30% chance of getting a reply
                    staff_user = random.choice(staff_users)
                    reply_days_ago = random.randint(0, days_ago - 1)  # Reply came after the rating
                    reply_date = timezone.now() - timedelta(days=reply_days_ago)
                    
                    reply = self.create_reply(rating, staff_user, reply_date)
                
                # Randomly add helpful marks
                self.add_helpful_marks(rating, customers, days_ago)
                    
    def get_weighted_rating(self, tendency):
        """Generate a rating value with some randomness but weighted toward the tendency"""
        # Calculate probabilities based on tendency
        if tendency >= 4.5:  # Excellent service
            weights = [0.01, 0.04, 0.15, 0.30, 0.50]  # 50% chance of 5-star
        elif tendency >= 4.0:  # Very good service
            weights = [0.02, 0.08, 0.20, 0.45, 0.25]  # 45% chance of 4-star
        elif tendency >= 3.5:  # Good service
            weights = [0.05, 0.10, 0.40, 0.30, 0.15]  # 40% chance of 3-star
        else:  # Average service
            weights = [0.10, 0.20, 0.40, 0.20, 0.10]  # Balanced
            
        # Choose rating based on weights
        return random.choices([1, 2, 3, 4, 5], weights=weights)[0]
    
    def generate_specific_ratings(self, model_class, overall_rating):
        """Generate specific category ratings based on the model type and overall rating"""
        # Base the specific ratings on the overall rating with some variation
        result = {}
        
        # Add some randomness but keep it close to the overall rating
        def get_varied_rating(base):
            variation = random.choice([-1, -0.5, 0, 0, 0, 0.5, 1])
            value = base + variation
            return max(1, min(5, value))  # Keep between 1-5
        
        # Common categories for all
        if model_class == Tour:
            result['value_rating'] = get_varied_rating(overall_rating)
            result['service_rating'] = get_varied_rating(overall_rating)
            result['knowledge_rating'] = get_varied_rating(overall_rating)
            result['cleanliness_rating'] = get_varied_rating(overall_rating)
            
        elif model_class == Park:
            result['cleanliness_rating'] = get_varied_rating(overall_rating)
            result['value_rating'] = get_varied_rating(overall_rating)
            result['service_rating'] = get_varied_rating(overall_rating)
            
        elif model_class == Guide:
            result['service_rating'] = get_varied_rating(overall_rating)
            result['knowledge_rating'] = get_varied_rating(overall_rating)
            result['value_rating'] = get_varied_rating(overall_rating)
            
        elif model_class == TourCompany:
            result['value_rating'] = get_varied_rating(overall_rating)
            result['service_rating'] = get_varied_rating(overall_rating)
            result['knowledge_rating'] = get_varied_rating(overall_rating)
            
        return result
    
    def create_reply(self, rating, staff_user, date):
        """Create a reply to a rating"""
        # Choose appropriate response based on the rating
        if rating.overall_rating >= 4:
            replies = [
                "Thank you for your wonderful feedback! We're delighted that you enjoyed your experience with us.",
                "We really appreciate your kind words! It's wonderful to hear that you had such a positive experience.",
                "Thank you for taking the time to share your experience. We're thrilled that you enjoyed your time with us!",
                "We're so happy that you had a great experience! Thank you for your lovely feedback."
            ]
        elif rating.overall_rating == 3:
            replies = [
                "Thank you for your feedback. We appreciate your comments and will work on improving the aspects you mentioned.",
                "Thank you for sharing your experience. We're sorry it wasn't perfect and are working to address the issues you raised.",
                "We appreciate your balanced review and take your suggestions seriously. We hope to serve you better next time.",
                "Thank you for your feedback. We're constantly working to improve our services and your comments help us do that."
            ]
        else:
            replies = [
                "We sincerely apologize for your disappointing experience. We would like to learn more about what went wrong so we can address these issues immediately.",
                "Thank you for bringing these issues to our attention. We're very sorry about your experience and would like to make it right.",
                "We apologize that your experience didn't meet expectations. Your feedback is important to us and we're taking steps to address the issues you've raised.",
                "We're sorry to hear about your experience. This is not the standard we aim for, and we would appreciate the opportunity to discuss this further."
            ]
            
        reply_text = random.choice(replies)
        
        # Add a personalized touch
        if random.random() < 0.5:
            if rating.overall_rating <= 2:
                reply_text += f" Please contact our customer service team at service@uwatours.com so we can address your concerns directly."
            else:
                reply_text += f" We hope to welcome you back again soon!"
                
        # Create the reply
        reply = RatingReply.objects.create(
            rating=rating,
            user=staff_user,
            comment=reply_text
        )
        
        # Set created date
        reply.created_at = date
        reply.save(update_fields=['created_at'])
        
        return reply
        
    def add_helpful_marks(self, rating, customers, max_days_ago):
        """Add helpful marks to a rating"""
        # Higher rated reviews tend to get more helpful marks
        if rating.overall_rating >= 4:
            num_helpful = random.randint(0, min(5, len(customers) - 1))  # Up to 5 helpful marks
        elif rating.overall_rating == 3:
            num_helpful = random.randint(0, min(3, len(customers) - 1))  # Up to 3 helpful marks
        else:
            num_helpful = random.randint(0, min(2, len(customers) - 1))  # Up to 2 helpful marks
            
        # Get distinct users different from the rating author
        potential_users = [c for c in customers if c != rating.user]
        if not potential_users:
            return
            
        # Select random users to mark as helpful
        helpful_users = random.sample(potential_users, min(num_helpful, len(potential_users)))
        
        for user in helpful_users:
            # Helpful mark comes after the rating
            days_ago = random.randint(0, max_days_ago - 1)
            mark_date = timezone.now() - timedelta(days=days_ago)
            
            helpful = RatingHelpful.objects.create(
                rating=rating,
                user=user
            )
            
            # Set created date
            helpful.created_at = mark_date
            helpful.save(update_fields=['created_at'])
