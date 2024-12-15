from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import pandas as pd
import numpy as np
from .models import Visualization, Dashboard, DashboardItem
from .serializers import VisualizationSerializer, DashboardSerializer, DashboardItemSerializer

class VisualizationViewSet(viewsets.ModelViewSet):
    """可视化视图集"""
    serializer_class = VisualizationSerializer
    queryset = Visualization.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """生成可视化数据"""
        visualization = self.get_object()
        try:
            if visualization.dataset:
                data = self._generate_dataset_visualization(visualization)
            elif visualization.training_session:
                data = self._generate_training_visualization(visualization)
            else:
                raise ValueError("必须指定数据集或训练会话")

            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _generate_dataset_visualization(self, visualization):
        """生成数据集可视化"""
        df = pd.read_csv(visualization.dataset.file.path)
        
        if visualization.chart_type == 'histogram':
            return self._generate_histogram(df, visualization.config)
        elif visualization.chart_type == 'scatter':
            return self._generate_scatter(df, visualization.config)
        elif visualization.chart_type == 'correlation':
            return self._generate_correlation(df, visualization.config)
        # 添加更多图表类型的处理...
        
        raise ValueError(f"不支持的图表类型: {visualization.chart_type}")

    def _generate_training_visualization(self, visualization):
        """生成训练过程可视化"""
        # 实现训练过程的可视化逻辑
        pass

    def _generate_histogram(self, df, config):
        """生成直方图数据"""
        column = config.get('column')
        bins = config.get('bins', 30)
        
        hist, bin_edges = np.histogram(df[column].dropna(), bins=bins)
        return {
            'type': 'histogram',
            'data': {
                'values': hist.tolist(),
                'bins': bin_edges.tolist(),
                'column': column
            }
        }

    def _generate_scatter(self, df, config):
        """生成散点图数据"""
        x_column = config.get('x_column')
        y_column = config.get('y_column')
        
        return {
            'type': 'scatter',
            'data': {
                'x': df[x_column].tolist(),
                'y': df[y_column].tolist(),
                'x_label': x_column,
                'y_label': y_column
            }
        }

    def _generate_correlation(self, df, config):
        """生成相关性矩阵数据"""
        columns = config.get('columns', df.select_dtypes(include=[np.number]).columns.tolist())
        corr_matrix = df[columns].corr().round(4)
        
        return {
            'type': 'correlation',
            'data': {
                'matrix': corr_matrix.to_dict(),
                'columns': columns
            }
        }

class DashboardViewSet(viewsets.ModelViewSet):
    """仪表板视图集"""
    serializer_class = DashboardSerializer
    queryset = Dashboard.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_visualization(self, request, pk=None):
        """添加可视��组件到仪表板"""
        dashboard = self.get_object()
        visualization_id = request.data.get('visualization_id')
        position = request.data.get('position', {'x': 0, 'y': 0})
        size = request.data.get('size', {'width': 6, 'height': 4})
        
        try:
            visualization = Visualization.objects.get(id=visualization_id)
            order = DashboardItem.objects.filter(dashboard=dashboard).count()
            
            item = DashboardItem.objects.create(
                dashboard=dashboard,
                visualization=visualization,
                position=position,
                size=size,
                order=order
            )
            
            return Response(DashboardItemSerializer(item).data)
        except Visualization.DoesNotExist:
            return Response(
                {'error': '可视化组件不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class DashboardItemViewSet(viewsets.ModelViewSet):
    """仪表板项目视图集"""
    serializer_class = DashboardItemSerializer
    queryset = DashboardItem.objects.all()

    @action(detail=True, methods=['post'])
    def update_position(self, request, pk=None):
        """更新组件位置"""
        item = self.get_object()
        position = request.data.get('position')
        size = request.data.get('size')
        
        if position:
            item.position = position
        if size:
            item.size = size
            
        item.save()
        return Response(DashboardItemSerializer(item).data) 