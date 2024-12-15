from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'datasets', views.DatasetViewSet, basename='dataset')
router.register(r'steps', views.PreprocessingStepViewSet, basename='preprocessing-step')
router.register(r'templates', views.PreprocessingTemplateViewSet, basename='preprocessing-template')

urlpatterns = [
    path('', include(router.urls)),
] 