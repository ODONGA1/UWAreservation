from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from .models import NotificationTemplate, NotificationLog, NotificationPreference


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template_type', 'channel', 'is_active', 
        'created_at', 'updated_at'
    ]
    list_filter = ['template_type', 'channel', 'is_active', 'created_at']
    search_fields = ['name', 'email_subject', 'sms_message']
    ordering = ['template_type', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'channel', 'is_active')
        }),
        ('Email Template', {
            'fields': ('email_subject', 'email_body_html', 'email_body_text'),
            'classes': ('collapse',)
        }),
        ('SMS Template', {
            'fields': ('sms_message',),
            'classes': ('collapse',)
        }),
        ('Template Variables', {
            'fields': ('available_variables',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'notification_id_short', 'recipient_display', 'channel', 
        'template_type_display', 'status_display', 'priority',
        'scheduled_at', 'sent_at', 'retry_count'
    ]
    list_filter = [
        'status', 'channel', 'priority', 'template__template_type',
        'scheduled_at', 'sent_at', 'created_at'
    ]
    search_fields = [
        'notification_id', 'recipient_email', 'recipient_phone',
        'recipient_user__username', 'recipient_user__email', 'subject'
    ]
    readonly_fields = [
        'notification_id', 'sent_at', 'delivered_at', 'created_at', 
        'updated_at', 'provider_message_id', 'provider_response'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Notification Details', {
            'fields': (
                'notification_id', 'template', 'channel', 'priority',
                'subject', 'message'
            )
        }),
        ('Recipient Information', {
            'fields': (
                'recipient_user', 'recipient_email', 'recipient_phone'
            )
        }),
        ('Related Objects', {
            'fields': ('related_booking_id', 'related_payment_id'),
            'classes': ('collapse',)
        }),
        ('Status & Timing', {
            'fields': (
                'status', 'scheduled_at', 'sent_at', 'delivered_at',
                'retry_count', 'max_retries'
            )
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Provider Information', {
            'fields': ('provider_message_id', 'provider_response'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def notification_id_short(self, obj):
        return str(obj.notification_id)[:8] + '...'
    notification_id_short.short_description = 'Notification ID'
    
    def recipient_display(self, obj):
        if obj.recipient_user:
            return f"{obj.recipient_user.username}"
        return obj.recipient_email or obj.recipient_phone
    recipient_display.short_description = 'Recipient'
    
    def template_type_display(self, obj):
        if obj.template:
            return obj.template.get_template_type_display()
        return '-'
    template_type_display.short_description = 'Type'
    
    def status_display(self, obj):
        colors = {
            'pending': '#ffc107',    # yellow
            'queued': '#17a2b8',     # info blue
            'sent': '#28a745',       # green
            'delivered': '#007bff',  # blue
            'failed': '#dc3545',     # red
            'bounced': '#6c757d',    # gray
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'recipient_user', 'template'
        )
    
    actions = ['resend_failed_notifications', 'mark_as_delivered']
    
    def resend_failed_notifications(self, request, queryset):
        """Resend failed notifications that can be retried"""
        from .tasks import send_email_notification, send_sms_notification
        
        resent_count = 0
        for notification in queryset.filter(status='failed'):
            if notification.can_retry:
                # Reset status and queue again
                notification.status = 'queued'
                notification.save()
                
                if notification.channel == 'email':
                    send_email_notification.delay(notification.id)
                else:
                    send_sms_notification.delay(notification.id)
                
                resent_count += 1
        
        self.message_user(request, f'{resent_count} notifications were queued for retry.')
    resend_failed_notifications.short_description = 'Resend failed notifications'
    
    def mark_as_delivered(self, request, queryset):
        """Mark notifications as delivered (for testing)"""
        updated = queryset.filter(status='sent').update(
            status='delivered',
            delivered_at=timezone.now()
        )
        self.message_user(request, f'{updated} notifications marked as delivered.')
    mark_as_delivered.short_description = 'Mark as delivered'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_notifications_enabled', 'sms_notifications_enabled',
        'preferred_email', 'preferred_phone', 'updated_at'
    ]
    list_filter = [
        'email_booking_confirmations', 'sms_booking_confirmations',
        'email_tour_reminders', 'sms_tour_reminders', 'updated_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'preferred_email', 'preferred_phone'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('preferred_email', 'preferred_phone')
        }),
        ('Email Preferences', {
            'fields': (
                'email_booking_confirmations', 'email_payment_confirmations',
                'email_tour_reminders', 'email_marketing'
            )
        }),
        ('SMS Preferences', {
            'fields': (
                'sms_booking_confirmations', 'sms_payment_confirmations',
                'sms_tour_reminders', 'sms_marketing'
            )
        }),
        ('Timing Preferences', {
            'fields': ('reminder_24h_before', 'reminder_2h_before')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def email_notifications_enabled(self, obj):
        enabled = any([
            obj.email_booking_confirmations,
            obj.email_payment_confirmations,
            obj.email_tour_reminders
        ])
        return format_html(
            '<span style="color: {};">{}</span>',
            '#28a745' if enabled else '#dc3545',
            '✓' if enabled else '✗'
        )
    email_notifications_enabled.short_description = 'Email'
    
    def sms_notifications_enabled(self, obj):
        enabled = any([
            obj.sms_booking_confirmations,
            obj.sms_payment_confirmations,
            obj.sms_tour_reminders
        ]) and obj.preferred_phone
        return format_html(
            '<span style="color: {};">{}</span>',
            '#28a745' if enabled else '#dc3545',
            '✓' if enabled else '✗'
        )
    sms_notifications_enabled.short_description = 'SMS'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
