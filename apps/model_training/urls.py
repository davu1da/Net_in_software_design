from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.TrainingSessionViewSet)
router.register(r'logs', views.TrainingLogViewSet)
router.register(r'checkpoints', views.ModelCheckpointViewSet)
router.register(r'deployed-models', views.DeployedModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 