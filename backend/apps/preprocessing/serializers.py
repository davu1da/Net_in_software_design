from rest_framework import serializers
from .models import Dataset, DatasetRow

class DatasetRowSerializer(serializers.ModelSerializer):
    """数据行序列化器"""
    class Meta:
        model = DatasetRow
        fields = ['id', 'data']

class DatasetSerializer(serializers.ModelSerializer):
    """数据集序列化器"""
    class Meta:
        model = Dataset
        fields = ['id', 'name', 'description', 'columns', 'created_at'] 