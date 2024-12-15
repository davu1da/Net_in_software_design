from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService

class NotificationViewSet(viewsets.ModelViewSet):
    """通知视图集"""
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """将所有通知标记为已读"""
        self.get_queryset().update(read=True)
        return Response({'message': '所有通知已标记为已读'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """将单个通知标记为已读"""
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'message': '通知已标记为已读'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        count = self.get_queryset().filter(read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """手动清理通知"""
        days = request.data.get('days', 30)
        read_only = request.data.get('read_only', True)
        
        try:
            deleted_count = NotificationService.cleanup_old_notifications(days, read_only)
            return Response({
                'message': f'成功清理 {deleted_count} 条通知',
                'deleted_count': deleted_count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取通知统计信息"""
        stats = NotificationService.get_notification_stats()
        return Response(stats) 