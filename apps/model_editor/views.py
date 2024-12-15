from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import NeuralNetwork, Layer, LayerConnection
from .serializers import (NeuralNetworkDetailSerializer, LayerConfigSerializer,
                         LayerConnectionSerializer)

class NeuralNetworkViewSet(viewsets.ModelViewSet):
    serializer_class = NeuralNetworkDetailSerializer
    
    def get_queryset(self):
        if not hasattr(self, 'request') or not self.request.user.is_authenticated:
            return NeuralNetwork.objects.none()
        return NeuralNetwork.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_layer(self, request, pk=None):
        """添加网络层"""
        network = self.get_object()
        serializer = LayerConfigSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(network=network)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def connect_layers(self, request, pk=None):
        """连接网络层"""
        network = self.get_object()
        serializer = LayerConnectionSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(network=network)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def validate_network(self, request, pk=None):
        """验证网络结构"""
        network = self.get_object()
        try:
            # 实现网络验证逻辑
            is_valid, message = self._validate_network_structure(network)
            return Response({
                'valid': is_valid,
                'message': message
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _validate_network_structure(self, network):
        """验证网络结构的具体实现"""
        layers = network.layers.all().order_by('order')
        connections = network.connections.all()
        
        # 检查是否有输入层和输出层
        has_input = any(layer.layer_type == 'input' for layer in layers)
        has_output = any(layer.layer_type == 'dense' for layer in layers)
        
        if not has_input:
            return False, "网络缺少输入层"
        if not has_output:
            return False, "网络缺少输出层"
            
        # 检查层间连接的有效性
        for conn in connections:
            if conn.from_layer.order >= conn.to_layer.order:
                return False, f"层 {conn.from_layer.name} 到 {conn.to_layer.name} 的连接形成了循环"
                
        return True, "网络结构有效"

class LayerViewSet(viewsets.ModelViewSet):
    serializer_class = LayerConfigSerializer
    
    def get_queryset(self):
        if not hasattr(self, 'request') or not self.request.user.is_authenticated:
            return Layer.objects.none()
        return Layer.objects.filter(network__owner=self.request.user)

class ConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = LayerConnectionSerializer
    
    def get_queryset(self):
        if not hasattr(self, 'request') or not self.request.user.is_authenticated:
            return LayerConnection.objects.none()
        return LayerConnection.objects.filter(network__owner=self.request.user)