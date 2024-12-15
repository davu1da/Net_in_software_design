from celery import shared_task
from .services import NotificationService

@shared_task
def cleanup_old_notifications(days=30, read_only=True):
    """清理旧通知的Celery任务"""
    deleted_count = NotificationService.cleanup_old_notifications(days, read_only)
    return f'已清理 {deleted_count} 条通知' 