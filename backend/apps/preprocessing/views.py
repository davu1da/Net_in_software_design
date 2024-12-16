from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Dataset, DatasetRow
from .serializers import DatasetSerializer, DatasetRowSerializer
from rest_framework.permissions import IsAuthenticated

class DataProcessingViewSet(viewsets.ModelViewSet):
    """数据处理视图集"""
    permission_classes = [IsAuthenticated]
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """获取数据集数据,支持分页和搜索"""
        try:
            dataset = self.get_object()
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            search = request.query_params.get('search', '')
            
            # 获取数据集的行
            queryset = dataset.rows.all()
            
            # 如果有搜索条件
            if search:
                queryset = queryset.filter(
                    Q(data__contains=search)
                )

            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            rows = queryset[start:end]

            return Response({
                'columns': dataset.columns,
                'data': [row.data for row in rows],
                'total': queryset.count()
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def update_rows(self, request, pk=None):
        """批量更新数据行"""
        dataset = self.get_object()
        changes = request.data.get('changes', [])
        
        try:
            for change in changes:
                row_id = change.get('id')
                row_changes = change.get('changes', {})
                
                row = DatasetRow.objects.get(id=row_id, dataset=dataset)
                for column, value in row_changes.items():
                    row.data[column] = value
                row.save()
                
            return Response({'message': '更新成功'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def delete_rows(self, request, pk=None):
        """批量删除数据行"""
        dataset = self.get_object()
        row_ids = request.data.get('row_ids', [])
        
        try:
            DatasetRow.objects.filter(
                id__in=row_ids,
                dataset=dataset
            ).delete()
            return Response({'message': '删除成功'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def add_row(self, request, pk=None):
        """添加新数据行"""
        dataset = self.get_object()
        row_data = request.data.get('data', {})
        
        try:
            row = DatasetRow.objects.create(
                dataset=dataset,
                data=row_data
            )
            return Response(DatasetRowSerializer(row).data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 