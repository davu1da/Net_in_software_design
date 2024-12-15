from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'visualizations', views.VisualizationViewSet)
router.register(r'dashboards', views.DashboardViewSet)
router.register(r'dashboard-items', views.DashboardItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 