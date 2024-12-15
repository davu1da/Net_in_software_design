from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    """通知模型"""
    LEVEL_CHOICES = (
        ('info', '信息'),
        ('success', '成功'),
        ('warning', '警告'),
        ('error', '错误'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="接收者")
    title = models.CharField(max_length=200, verbose_name="标题")
    message = models.TextField(verbose_name="消息内容")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info', verbose_name="级别")
    read = models.BooleanField(default=False, verbose_name="是否已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    # 通用关联
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}" 