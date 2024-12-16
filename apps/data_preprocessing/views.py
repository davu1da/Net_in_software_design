from rest_framework import viewsets, status
from rest_framework.decorators import action, parser_classes
from rest_framework.response import Response
from .models import Dataset, PreprocessingStep, ProcessedDataset, PreprocessingTemplate
from .serializers import (DatasetSerializer, PreprocessingStepSerializer,
                         ProcessedDatasetSerializer, PreprocessingTemplateSerializer)
from .services import DataPreprocessingService
import pandas as pd
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    
    def get_queryset(self):
        return Dataset.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        dataset = serializer.save(owner=self.request.user)
        
        # 读取并分析数据集
        df = DataPreprocessingService.read_dataset(
            dataset.file.path,
            dataset.file_type
        )
        info = DataPreprocessingService.get_dataset_info(df)
        
        # 更新数据集信息
        dataset.columns = info['columns']
        dataset.row_count = info['row_count']
        dataset.save()

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """预览数据集"""
        dataset = self.get_object()
        try:
            df = DataPreprocessingService.read_dataset(
                dataset.file.path,
                dataset.file_type
            )
            return Response({
                'head': df.head().to_dict(),
                'columns': dataset.columns
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PreprocessingStepViewSet(viewsets.ModelViewSet):
    serializer_class = PreprocessingStepSerializer
    
    def get_queryset(self):
        return PreprocessingStep.objects.filter(
            dataset__owner=self.request.user
        )

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """执行预处理步骤"""
        step = self.get_object()
        service = DataPreprocessingService()
        
        try:
            # 更新状态为执行中
            step.status = 'running'
            step.save()

            # 读取数据
            df = service.read_dataset(
                step.dataset.file.path,
                step.dataset.file_type
            )

            # 根据步骤类型执行相应的预处理
            if step.step_type == 'clean':
                df = service.clean_data(df, step.parameters)
                result = service.get_dataset_info(df)
            elif step.step_type == 'transform':
                df = service.transform_data(df, step.parameters)
                result = service.get_dataset_info(df)
            elif step.step_type == 'encode':
                df, encoders = service.encode_data(df, step.parameters)
                result = {
                    'info': service.get_dataset_info(df),
                    'encoders': {k: v.classes_.tolist() for k, v in encoders.items()}
                }
            elif step.step_type == 'scale':
                df, scalers = service.scale_data(df, step.parameters)
                result = service.get_dataset_info(df)
            elif step.step_type == 'split':
                split_data = service.split_data(df, step.parameters)
                # 保存分割后的数据集
                save_path = f'processed_datasets/{step.dataset.id}/'
                paths = service.save_processed_data(
                    split_data,
                    save_path,
                    step.dataset.name
                )
                result = {
                    'paths': paths,
                    'shapes': {
                        k: {'X': v[0].shape, 'y': v[1].shape}
                        for k, v in split_data.items()
                    }
                }

            # 更新步骤状态和结果
            step.status = 'completed'
            step.result = result
            step.save()

            return Response({
                'status': 'completed',
                'result': result
            })

        except Exception as e:
            step.status = 'failed'
            step.result = {'error': str(e)}
            step.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 

class PreprocessingTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = PreprocessingTemplateSerializer
    
    def get_queryset(self):
        """获取用户可见的模板列表"""
        return PreprocessingTemplate.objects.filter(
            Q(owner=self.request.user) | Q(is_public=True)
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """应用模板到指定数据集"""
        template = self.get_object()
        dataset_id = request.data.get('dataset_id')
        
        try:
            dataset = Dataset.objects.get(id=dataset_id, owner=request.user)
            
            # 创建预处理步骤
            for step_data in template.steps:
                PreprocessingStep.objects.create(
                    dataset=dataset,
                    name=step_data['name'],
                    step_type=step_data['step_type'],
                    parameters=step_data['parameters']
                )
            
            return Response({'message': '模板应用成功'})
        except Dataset.DoesNotExist:
            return Response(
                {'error': '数据集不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 

@parser_classes([MultiPartParser, FormParser])
class FileUploadView(APIView):
    permission_classes = [AllowAny]  # 临时允许匿名访问，测试用
    
    def post(self, request):
        try:
            # 检查用户认证状态
            if not request.user.is_authenticated:
                return Response(
                    {'message': '请先登录'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            file_obj = request.FILES['file']
            dataset = Dataset.objects.create(
                file=file_obj,
                owner=request.user,
                name=file_obj.name,
                file_type=file_obj.name.split('.')[-1].lower()
            )
            
            return Response({
                'message': '文件上传成功',
                'dataset': DatasetSerializer(dataset).data
            })
        except Exception as e:
            return Response(
                {'message': f'文件上传失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )