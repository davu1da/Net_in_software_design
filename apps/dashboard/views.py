from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.model_training.models import TrainingSession
from apps.data_preprocessing.models import Dataset
from apps.notifications.models import Notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_statistics(request):
    """获取仪表板统计数据"""
    statistics = {
        'datasetsCount': Dataset.objects.filter(owner=request.user).count(),
        'modelsCount': TrainingSession.objects.filter(owner=request.user).count(),
        'activeTrainings': TrainingSession.objects.filter(
            owner=request.user, 
            status='running'
        ).count(),
        'deployedModels': TrainingSession.objects.filter(
            owner=request.user,
            status='completed'
        ).count()
    }
    return Response(statistics)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """获取用户通知"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]
    
    return Response([{
        'id': notification.id,
        'message': notification.message,
        'type': notification.notification_type,
        'read': notification.read,
        'created_at': notification.created_at
    } for notification in notifications]) 