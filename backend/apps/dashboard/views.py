from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_statistics(request):
    """获取仪表盘统计数据"""
    try:
        # 这里添加实际的统计逻辑
        statistics = {
            'datasets': 0,  # Dataset.objects.count()
            'models': 0,    # Model.objects.count()
            'trainings': 0  # Training.objects.count()
        }
        return Response(statistics)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """获取系统通知"""
    try:
        notifications = []  # 从数据库获取通知
        return Response(notifications)
    except Exception as e:
        return Response({'error': str(e)}, status=500) 