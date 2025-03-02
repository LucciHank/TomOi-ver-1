from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    verbose_name = 'Admin Dashboard'
    
    def ready(self):
        # Ngăn chặn việc đăng ký model nhiều lần
        import sys
        if 'runserver' not in sys.argv:
            return True
        
        # Import signals
        import dashboard.signals