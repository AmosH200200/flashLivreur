# app_notifications/apps.py
from django.apps import AppConfig

class AppNotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_notifications' 

    def ready(self):
        import app_notifications.signals 