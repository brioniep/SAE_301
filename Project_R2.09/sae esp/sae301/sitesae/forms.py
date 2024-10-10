from django.apps import AppConfig
from django import forms
from .models import Schedule

class SitesaeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sitesae'


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['start_time', 'end_time', 'prise_id']
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M'),
            'end_time': forms.TimeInput(format='%H:%M'),
        }
