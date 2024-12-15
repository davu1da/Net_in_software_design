from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'networks', views.NeuralNetworkViewSet, basename='network')
router.register(r'layers', views.LayerViewSet, basename='layer')
router.register(r'connections', views.ConnectionViewSet, basename='connection')

urlpatterns = [
    path('', include(router.urls)),
] 