from rest_framework import serializers
from .models import Dataset, PreprocessingStep, ProcessedDataset, PreprocessingTemplate

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'name', 'description', 'file_type', 'columns', 
                 'row_count', 'created_at', 'updated_at']
        read_only_fields = ['columns', 'row_count']

class PreprocessingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessingStep
        fields = ['id', 'name', 'step_type', 'parameters', 'order', 
                 'status', 'result', 'created_at']
        read_only_fields = ['status', 'result']

class ProcessedDatasetSerializer(serializers.ModelSerializer):
    preprocessing_steps = PreprocessingStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProcessedDataset
        fields = ['id', 'name', 'original_dataset', 'preprocessing_steps',
                 'columns', 'row_count', 'created_at']
        read_only_fields = ['columns', 'row_count']

class PreprocessingTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessingTemplate
        fields = ['id', 'name', 'description', 'steps', 
                 'created_at', 'updated_at', 'is_public']
        read_only_fields = ['created_at', 'updated_at']