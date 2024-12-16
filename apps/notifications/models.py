from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', '信息'),
        ('success', '成功'),
        ('warning', '警告'),
        ('error', '错误'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="接收者")
    message = models.TextField(verbose_name="通知内容")
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='info',
        verbose_name="通知类型"
    )
    read = models.BooleanField(default=False, verbose_name="是否已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "系统通知"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.message}" 