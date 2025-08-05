# Availability Management Views - to be appended to tours/views.py

@user_passes_test(can_manage_parks, login_url='tours:tour_list')
def add_availability(request, tour_id):
    """Add new availability for a tour"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            tour = get_object_or_404(Tour, id=tour_id)
            guide_id = data.get('guide_id')
            guide = None
            if guide_id:
                from tours.models import Guide
                guide = get_object_or_404(Guide, id=guide_id)
            
            availability = Availability.objects.create(
                tour=tour,
                date=data['date'],
                slots_available=data['slots_available'],
                guide=guide
            )
            
            return JsonResponse({
                'success': True,
                'availability': {
                    'id': availability.id,
                    'date': availability.date.strftime('%Y-%m-%d'),
                    'slots_available': availability.slots_available,
                    'guide_name': availability.guide.user.get_full_name() if availability.guide else 'No guide assigned'
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@user_passes_test(can_manage_parks, login_url='tours:tour_list')
def edit_availability(request, availability_id):
    """Edit existing availability"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            availability = get_object_or_404(Availability, id=availability_id)
            
            guide_id = data.get('guide_id')
            guide = None
            if guide_id:
                from tours.models import Guide
                guide = get_object_or_404(Guide, id=guide_id)
            
            availability.date = data['date']
            availability.slots_available = data['slots_available']
            availability.guide = guide
            availability.save()
            
            return JsonResponse({
                'success': True,
                'availability': {
                    'id': availability.id,
                    'date': availability.date.strftime('%Y-%m-%d'),
                    'slots_available': availability.slots_available,
                    'guide_name': availability.guide.user.get_full_name() if availability.guide else 'No guide assigned'
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@user_passes_test(can_manage_parks, login_url='tours:tour_list')
def delete_availability(request, availability_id):
    """Delete availability"""
    if request.method == 'DELETE':
        try:
            availability = get_object_or_404(Availability, id=availability_id)
            availability.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
