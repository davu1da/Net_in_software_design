from rest_framework import serializers
from .models import Visualization, Dashboard, DashboardItem

class VisualizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visualization
        fields = ['id', 'name', 'description', 'chart_type', 'dataset', 
                 'training_session', 'config', 'created_at', 'updated_at', 'owner']
        read_only_fields = ['created_at', 'updated_at', 'owner']

class DashboardItemSerializer(serializers.ModelSerializer):
    visualization_data = VisualizationSerializer(source='visualization', read_only=True)

    class Meta:
        model = DashboardItem
        fields = ['id', 'dashboard', 'visualization', 'visualization_data', 
                 'position', 'size', 'order']

class DashboardSerializer(serializers.ModelSerializer):
    items = DashboardItemSerializer(source='dashboarditem_set', many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = ['id', 'name', 'description', 'layout', 'created_at', 
                 'updated_at', 'owner', 'items']
        read_only_fields = ['created_at', 'updated_at', 'owner'] 