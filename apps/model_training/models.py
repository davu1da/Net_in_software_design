from django.db import models
from django.contrib.auth.models import User
from apps.model_editor.models import NeuralNetwork
from apps.data_preprocessing.models import Dataset

class TrainingSession(models.Model):
    """训练会话模型"""
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('running', '训练中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('stopped', '已停止'),
    )

    name = models.CharField(max_length=200, verbose_name="会话名称")
    description = models.TextField(blank=True, verbose_name="描述")
    network = models.ForeignKey(NeuralNetwork, on_delete=models.CASCADE, verbose_name="神经网络")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, verbose_name="训练数据集")
    validation_dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, blank=True, 
                                         related_name='validation_sessions', verbose_name="验证数据集")
    hyperparameters = models.JSONField(verbose_name="超参数配置")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    metrics = models.JSONField(default=dict, verbose_name="训练指标")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")

    class Meta:
        verbose_name = "训练会话"
        verbose_name_plural = verbose_name

class TrainingLog(models.Model):
    """训练日志模型"""
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, verbose_name="训练会话")
    epoch = models.IntegerField(verbose_name="训练轮次")
    metrics = models.JSONField(verbose_name="训练指标")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "训练日志"
        verbose_name_plural = verbose_name
        ordering = ['epoch']

class ModelCheckpoint(models.Model):
    """模型检查点模型"""
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, verbose_name="训练会话")
    epoch = models.IntegerField(verbose_name="保存轮次")
    file = models.FileField(upload_to='checkpoints/', verbose_name="检查点文件")
    metrics = models.JSONField(verbose_name="检查点指标")
    is_best = models.BooleanField(default=False, verbose_name="是否最佳")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "模型检查点"
        verbose_name_plural = verbose_name
        ordering = ['-epoch']

class DeployedModel(models.Model):
    """已部署模型"""
    STATUS_CHOICES = (
        ('active', '运行中'),
        ('inactive', '已停止'),
        ('error', '错误'),
    )

    name = models.CharField(max_length=200, verbose_name="部署名称")
    description = models.TextField(blank=True, verbose_name="描述")
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, verbose_name="训练会话")
    checkpoint = models.ForeignKey(
        ModelCheckpoint, 
        on_delete=models.CASCADE, 
        verbose_name="使用的检查点",
        null=True,
        blank=True
    )
    endpoint_url = models.URLField(verbose_name="服务端点URL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name="状态")
    config = models.JSONField(verbose_name="部署配置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")

    class Meta:
        verbose_name = "已部署模型"
        verbose_name_plural = verbose_name 