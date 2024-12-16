from django.db import models
from django.contrib.postgres.fields import JSONField

class Dataset(models.Model):
    """数据集模型"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    columns = JSONField()  # 存储列信息
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class DatasetRow(models.Model):
    """数据行模型"""
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='rows'
    )
    data = JSONField()  # 存储行数据
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id'] 