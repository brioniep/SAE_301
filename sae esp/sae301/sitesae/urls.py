from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Page d'accueil
    path('temperature/', views.get_temperature, name='get_temperature'),  # Affichage des températures
    path('on/<int:prise_id>/', views.turn_on, name='turn_on'),  # Allumer une prise spécifique
    path('off/<int:prise_id>/', views.turn_off, name='turn_off'),  # Éteindre une prise spécifique
    path('all/on/', views.turn_on_all, name='turn_on_all'),  # Allumer les deux prises
    path('all/off/', views.turn_off_all, name='turn_off_all'),  # Éteindre les deux prises
    path('schedule/', views.schedule, name='schedule'),  # Planifier les plages horaires
]
