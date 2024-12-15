from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/preprocessing/', include('apps.data_preprocessing.urls')),
    path('api/editor/', include('apps.model_editor.urls')),
    path('api/training/', include('apps.model_training.urls')),
    path('api/visualization/', include('apps.visualization.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 