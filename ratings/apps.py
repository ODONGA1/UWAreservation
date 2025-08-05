from django.apps import AppConfig


class RatingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ratings'
    
    def ready(self):
        # Import signal handlers
        import ratings.signals
