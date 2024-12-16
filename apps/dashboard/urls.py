from django.urls import path
from . import views

urlpatterns = [
    path('statistics/', views.get_dashboard_statistics, name='dashboard-statistics'),
    path('notifications/', views.get_notifications, name='dashboard-notifications'),
] 