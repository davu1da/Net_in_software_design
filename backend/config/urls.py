from django.urls import path, include

urlpatterns = [
    # ... 其他 URL patterns ...
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/preprocessing/', include('apps.preprocessing.urls')),
    path('api/training/', include('apps.training.urls')),
] 