from django.apps import AppConfig
from django import forms
from .models import Schedule


class SitesaeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sitesae'


class ScheduleForm(forms.ModelForm):
    email = forms.EmailField(label='Adresse email', required=True)
    phone = forms.CharField(label='Numéro de téléphone', required=False)
    

    class Meta:
        model = Schedule
        fields = ['email', 'phone', 'prise_id', 'start_time', 'end_time', 'temperature_threshold']  
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M'),
            'end_time': forms.TimeInput(format='%H:%M'),
    
            
        }
    
