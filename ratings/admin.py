from django.contrib import admin
from django.utils.html import format_html
from .models import Rating, RatingPhoto, RatingReply, RatingHelpful


class RatingPhotoInline(admin.TabularInline):
    model = RatingPhoto
    extra = 0
    fields = ('photo', 'caption', 'created_at')
    readonly_fields = ('created_at',)


class RatingReplyInline(admin.TabularInline):
    model = RatingReply
    extra = 0
    fields = ('user', 'comment', 'created_at')
    readonly_fields = ('created_at',)


class RatingHelpfulInline(admin.TabularInline):
    model = RatingHelpful
    extra = 0
    fields = ('user', 'is_helpful', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_link', 'overall_rating', 'is_verified', 
                   'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_verified', 'is_featured', 'created_at', 'content_type')
    search_fields = ('user__username', 'user__email', 'comment')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)
    inlines = [RatingPhotoInline, RatingReplyInline, RatingHelpfulInline]
    
    fieldsets = (
        ('Rating Information', {
            'fields': (
                'user', 
                ('content_type', 'object_id'), 
                'comment',
            ),
        }),
        ('Rating Values', {
            'fields': (
                'overall_rating',
                ('value_rating', 'service_rating'),
                ('cleanliness_rating', 'knowledge_rating'),
            ),
        }),
        ('Status', {
            'fields': (
                ('status', 'is_verified', 'is_featured'),
                ('created_at', 'updated_at'),
            ),
        }),
    )
    
    def object_link(self, obj):
        """Create a link to the rated object if possible"""
        content_object = obj.content_object
        if content_object:
            object_name = str(content_object)
            try:
                # Try to get the admin change URL for the object
                from django.urls import reverse
                url = reverse(
                    f'admin:{content_object._meta.app_label}_{content_object._meta.model_name}_change',
                    args=[content_object.pk]
                )
                return format_html('<a href="{}">{}</a>', url, object_name)
            except:
                return object_name
        return '-'
    
    object_link.short_description = 'Rated Object'


@admin.register(RatingPhoto)
class RatingPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'rating', 'photo_thumbnail', 'caption', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('rating__user__username', 'caption')
    raw_id_fields = ('rating',)
    
    def photo_thumbnail(self, obj):
        """Display a thumbnail of the photo"""
        if obj.photo:
            return format_html('<img src="{}" height="50" />', obj.photo.url)
        return '-'
    
    photo_thumbnail.short_description = 'Photo'


@admin.register(RatingReply)
class RatingReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'rating', 'user', 'comment_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('rating__user__username', 'user__username', 'comment')
    raw_id_fields = ('rating', 'user')
    
    def comment_preview(self, obj):
        """Show a preview of the comment"""
        if obj.comment:
            return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
        return '-'
    
    comment_preview.short_description = 'Comment'
