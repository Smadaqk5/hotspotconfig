from django.apps import AppConfig

class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscriptions'
    
    def ready(self):
        from django.contrib import admin
        from .admin_dashboard import add_dashboard_to_admin
        add_dashboard_to_admin(admin.site)
