from rest_framework import serializers
from .models import NeuralNetwork, Layer, LayerConnection

class LayerConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layer
        fields = ['id', 'name', 'layer_type', 'config', 'order']

class LayerConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayerConnection
        fields = ['id', 'from_layer', 'to_layer']

class NeuralNetworkDetailSerializer(serializers.ModelSerializer):
    layers = LayerConfigSerializer(many=True, read_only=True)
    connections = LayerConnectionSerializer(many=True, read_only=True)

    class Meta:
        model = NeuralNetwork
        fields = ['id', 'name', 'description', 'layers', 
                 'connections', 'created_at', 'updated_at', 'owner']