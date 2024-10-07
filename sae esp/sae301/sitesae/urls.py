from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='sitesae/index'),
    path('login/', views.login_view, name='sitesae/login'),
    path('logout/', views.logout_view, name='sitesae/logout'),
    path('temperature/', views.get_temperature, name='temperature'),
    path('turn_on/<int:prise_id>/', views.turn_on, name='turn_on'),
    path('turn_off/<int:prise_id>/', views.turn_off, name='turn_off'),
    path('turn_on_all/', views.turn_on_all, name='turn_on_all'),
    path('turn_off_all/', views.turn_off_all, name='turn_off_all'),
]

