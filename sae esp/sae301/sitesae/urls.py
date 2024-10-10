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
    path('enforce_schedules/', views.enforce_schedules, name='enforce_schedules'),
    path('add_schedule/', views.add_schedule, name='add_schedule'),
    path('delete_schedule/<int:schedule_id>/', views.delete_schedule, name='sitesae/delete_schedule'),
    path('delete_all_schedules/', views.delete_all_schedules, name='sitesae/delete_all_schedules'),
    path('led_status/', views.get_led_status, name='led_status'),
]

