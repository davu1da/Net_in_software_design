from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataProcessingViewSet

router = DefaultRouter()
router.register(r'datasets', DataProcessingViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 