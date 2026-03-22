from django.urls import path
from . import views

urlpatterns = [
    path('', views.machine_list, name='machine_list'),
    path('machine/<int:machine_id>/', views.play_machine, name='play_machine'),
    path('machine/<int:machine_id>/spin/', views.spin, name='spin'),
    path('history/', views.history, name='history'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('login') 
path('logout/', views.user_logout, name='logout'),