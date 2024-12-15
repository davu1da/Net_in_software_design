from rest_framework import serializers
from .models import TrainingSession, TrainingLog, ModelCheckpoint, DeployedModel

class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = ['id', 'name', 'description', 'network', 'dataset', 
                 'validation_dataset', 'hyperparameters', 'status', 'metrics',
                 'created_at', 'started_at', 'completed_at', 'owner']
        read_only_fields = ['status', 'metrics', 'created_at', 
                           'started_at', 'completed_at', 'owner']

class TrainingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingLog
        fields = ['id', 'session', 'epoch', 'metrics', 'created_at']
        read_only_fields = ['created_at']

class ModelCheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCheckpoint
        fields = ['id', 'session', 'epoch', 'file', 'metrics', 
                 'is_best', 'created_at']
        read_only_fields = ['created_at']

class DeployedModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeployedModel
        fields = ['id', 'name', 'description', 'session', 'checkpoint',
                 'endpoint_url', 'status', 'config', 'created_at', 
                 'updated_at', 'owner']
        read_only_fields = ['status', 'created_at', 'updated_at', 'owner'] 