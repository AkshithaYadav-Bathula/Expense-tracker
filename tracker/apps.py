from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'
    verbose_name = 'Expense Tracker'
    
    def ready(self):
        # Import signals here to ensure they are registered
        try:
            import tracker.signals
        except ImportError:
            pass