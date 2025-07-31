from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Availability, Booking, Payment, BookingNotification


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['tour', 'date', 'slots_available', 'guide', 'is_available_display', 'created_at']
    list_filter = ['date', 'tour__park', 'guide']
    search_fields = ['tour__name', 'tour__park__name', 'guide__user__username']
    date_hierarchy = 'date'
    ordering = ['date']
    
    def is_available_display(self, obj):
        if obj.is_past_date:
            return format_html('<span style="color: gray;">Past Date</span>')
        elif obj.is_available:
            return format_html('<span style="color: green;">Available</span>')
        else:
            return format_html('<span style="color: red;">Full</span>')
    is_available_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tour', 'tour__park', 'guide', 'guide__user')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_id_short', 'tourist', 'tour_info', 'date', 'num_of_people', 
        'total_cost', 'booking_status_display', 'payment_status_display', 'booking_date'
    ]
    list_filter = ['booking_status', 'payment_status', 'booking_date', 'availability__date']
    search_fields = [
        'booking_id', 'tourist__username', 'tourist__email', 
        'availability__tour__name', 'contact_email'
    ]
    readonly_fields = ['booking_id', 'booking_date', 'confirmed_at', 'cancelled_at']
    date_hierarchy = 'booking_date'
    ordering = ['-booking_date']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'tourist', 'availability', 'num_of_people')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'total_cost')
        }),
        ('Status', {
            'fields': ('booking_status', 'payment_status')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Additional Information', {
            'fields': ('special_requirements',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('booking_date', 'confirmed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    def booking_id_short(self, obj):
        return str(obj.booking_id)[:8] + '...'
    booking_id_short.short_description = 'Booking ID'
    
    def tour_info(self, obj):
        return f"{obj.availability.tour.name} - {obj.availability.tour.park.name}"
    tour_info.short_description = 'Tour'
    
    def date(self, obj):
        return obj.availability.date
    date.short_description = 'Tour Date'
    
    def booking_status_display(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'completed': 'blue',
            'refunded': 'purple'
        }
        color = colors.get(obj.booking_status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_booking_status_display()
        )
    booking_status_display.short_description = 'Booking Status'
    
    def payment_status_display(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'purple'
        }
        color = colors.get(obj.payment_status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'Payment Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tourist', 'availability', 'availability__tour', 'availability__tour__park'
        )
    
    actions = ['confirm_selected_bookings', 'cancel_selected_bookings']
    
    def confirm_selected_bookings(self, request, queryset):
        confirmed_count = 0
        for booking in queryset:
            if booking.confirm_booking():
                confirmed_count += 1
        self.message_user(request, f'{confirmed_count} bookings were confirmed.')
    confirm_selected_bookings.short_description = 'Confirm selected bookings'
    
    def cancel_selected_bookings(self, request, queryset):
        cancelled_count = 0
        for booking in queryset:
            if booking.cancel_booking():
                cancelled_count += 1
        self.message_user(request, f'{cancelled_count} bookings were cancelled.')
    cancel_selected_bookings.short_description = 'Cancel selected bookings'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id_short', 'booking_link', 'payment_method', 
        'amount', 'currency', 'status_display', 'initiated_at'
    ]
    list_filter = ['payment_method', 'status', 'currency', 'initiated_at']
    search_fields = [
        'payment_id', 'booking__booking_id', 'gateway_transaction_id', 
        'gateway_reference', 'booking__tourist__username'
    ]
    readonly_fields = ['payment_id', 'initiated_at', 'completed_at']
    date_hierarchy = 'initiated_at'
    ordering = ['-initiated_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'booking', 'payment_method', 'amount', 'currency')
        }),
        ('Gateway Information', {
            'fields': ('gateway_transaction_id', 'gateway_reference'),
            'classes': ('collapse',)
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'initiated_at', 'completed_at')
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
    )
    
    def payment_id_short(self, obj):
        return str(obj.payment_id)[:8] + '...'
    payment_id_short.short_description = 'Payment ID'
    
    def booking_link(self, obj):
        url = reverse('admin:booking_booking_change', args=[obj.booking.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.booking.booking_id)[:8] + '...')
    booking_link.short_description = 'Booking'
    
    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'booking__tourist')


@admin.register(BookingNotification)
class BookingNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'booking_link', 'notification_type', 'method', 
        'delivery_status', 'delivery_attempts', 'sent_at'
    ]
    list_filter = ['notification_type', 'method', 'delivered', 'sent_at']
    search_fields = ['booking__booking_id', 'subject', 'booking__tourist__username']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'
    ordering = ['-sent_at']
    
    def booking_link(self, obj):
        url = reverse('admin:booking_booking_change', args=[obj.booking.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.booking.booking_id)[:8] + '...')
    booking_link.short_description = 'Booking'
    
    def delivery_status(self, obj):
        if obj.delivered:
            return format_html('<span style="color: green;">Delivered</span>')
        else:
            return format_html('<span style="color: red;">Failed</span>')
    delivery_status.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'booking__tourist')
