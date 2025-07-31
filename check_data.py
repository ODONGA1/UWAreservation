from booking.models import Availability
from tours.models import Guide

print("Checking availabilities...")
availabilities = Availability.objects.all()[:5]
for a in availabilities:
    print(f"Tour: {a.tour.name}")
    print(f"Date: {a.date}")
    print(f"Slots: {a.slots_available}")
    if a.guide:
        print(f"Guide: {a.guide.user.username}")
        print(f"Guide full name: '{a.guide.user.get_full_name()}'")
        print(f"Guide first name: '{a.guide.user.first_name}'")
        print(f"Guide last name: '{a.guide.user.last_name}'")
    else:
        print("No guide assigned")
    print("---")
