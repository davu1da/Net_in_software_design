from django.db import models
from django.contrib.auth.models import User

class Dataset(models.Model):
    """数据集模型"""
    name = models.CharField(max_length=200, verbose_name="数据集名称")
    description = models.TextField(blank=True, verbose_name="数据集描述")
    file = models.FileField(upload_to='datasets/', verbose_name="数据文件")
    file_type = models.CharField(max_length=20, choices=[
        ('csv', 'CSV文件'),
        ('excel', 'Excel文件'),
        ('json', 'JSON文件')
    ], verbose_name="文件类型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")
    columns = models.JSONField(default=list, verbose_name="列信息")
    row_count = models.IntegerField(default=0, verbose_name="行数")
    
    class Meta:
        verbose_name = "数据集"
        verbose_name_plural = verbose_name

class PreprocessingStep(models.Model):
    """预处理步骤模型"""
    STEP_TYPES = (
        ('clean', '数据清洗'),
        ('transform', '数据转换'),
        ('encode', '编码转换'),
        ('scale', '数据缩放'),
        ('split', '数据分割')
    )

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='preprocessing_steps')
    name = models.CharField(max_length=100, verbose_name="步骤名称")
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, verbose_name="步骤类型")
    parameters = models.JSONField(verbose_name="步骤参数")
    order = models.IntegerField(verbose_name="执行顺序")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败')
    ], default='pending')
    result = models.JSONField(null=True, blank=True, verbose_name="执行结果")

    class Meta:
        verbose_name = "预处理步骤"
        verbose_name_plural = verbose_name
        ordering = ['order']

class ProcessedDataset(models.Model):
    """处理后的数据集"""
    original_dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='processed_versions')
    name = models.CharField(max_length=200, verbose_name="��理后数据集名称")
    file = models.FileField(upload_to='processed_datasets/', verbose_name="处理后文件")
    preprocessing_steps = models.ManyToManyField(PreprocessingStep, related_name='resulting_datasets')
    created_at = models.DateTimeField(auto_now_add=True)
    columns = models.JSONField(default=list, verbose_name="处理后列信息")
    row_count = models.IntegerField(default=0, verbose_name="处理后行数")
    
    class Meta:
        verbose_name = "处理后数据集"
        verbose_name_plural = verbose_name

class PreprocessingTemplate(models.Model):
    """预处理模板模型"""
    name = models.CharField(max_length=100, verbose_name="模板名称")
    description = models.TextField(blank=True, verbose_name="模板描述")
    steps = models.JSONField(verbose_name="预处理步骤")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    
    class Meta:
        verbose_name = "预处理模板"
        verbose_name_plural = verbose_name