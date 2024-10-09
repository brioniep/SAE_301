from django.apps import AppConfig
from django import forms

class SitesaeConfig(AppConfig):
    name = 'sitesae'

    def ready(self):
        # Import signals or other initialization logic here
        pass

class SitesaeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sitesae'

    def ready(self):
        from .views import start_schedule_checker
        start_schedule_checker()