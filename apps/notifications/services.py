from django.contrib.contenttypes.models import ContentType
from .models import Notification
from django.utils import timezone
from datetime import timedelta

class NotificationService:
    @staticmethod
    def create_notification(recipient, title, message, level='info', related_object=None):
        """创建新通知"""
        notification = Notification(
            recipient=recipient,
            title=title,
            message=message,
            level=level
        )
        
        if related_object:
            notification.content_type = ContentType.objects.get_for_model(related_object)
            notification.object_id = related_object.id
            
        notification.save()
        return notification

    @staticmethod
    def create_training_notification(training_session):
        """创建训练相关通知"""
        if training_session.status == 'completed':
            message = f"模型 '{training_session.network.name}' 训练已完成"
            level = 'success'
        elif training_session.status == 'failed':
            message = f"模型 '{training_session.network.name}' 训练失败"
            level = 'error'
        else:
            return None

        return NotificationService.create_notification(
            recipient=training_session.owner,
            title=f"训练状态更新",
            message=message,
            level=level,
            related_object=training_session
        )

    @staticmethod
    def create_model_deployment_notification(deployed_model):
        """创建模型部署相关通知"""
        if deployed_model.status == 'active':
            message = f"模型 '{deployed_model.session.network.name}' 已成功部署"
            level = 'success'
        elif deployed_model.status == 'error':
            message = f"模型 '{deployed_model.session.network.name}' 部署失败"
            level = 'error'
        else:
            return None

        return NotificationService.create_notification(
            recipient=deployed_model.owner,
            title=f"模型部署状态",
            message=message,
            level=level,
            related_object=deployed_model
        )

    @staticmethod
    def cleanup_old_notifications(days=30, read_only=True):
        """清理旧通知"""
        cutoff_date = timezone.now() - timedelta(days=days)
        query = {'created_at__lt': cutoff_date}
        
        if read_only:
            query['read'] = True
            
        return Notification.objects.filter(**query).delete()

    @staticmethod
    def get_notification_stats():
        """获取通知统计信息"""
        total = Notification.objects.count()
        unread = Notification.objects.filter(read=False).count()
        oldest = Notification.objects.order_by('created_at').first()
        newest = Notification.objects.order_by('-created_at').first()
        
        return {
            'total_count': total,
            'unread_count': unread,
            'oldest_date': oldest.created_at if oldest else None,
            'newest_date': newest.created_at if newest else None
        } 