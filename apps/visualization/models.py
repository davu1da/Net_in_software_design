from django.db import models
from django.contrib.auth.models import User
from apps.data_preprocessing.models import Dataset
from apps.model_training.models import TrainingSession

class Visualization(models.Model):
    """可视化配置模型"""
    CHART_TYPES = (
        ('line', '折线图'),
        ('bar', '柱状图'),
        ('scatter', '散点图'),
        ('histogram', '直方图'),
        ('heatmap', '热力图'),
        ('box', '箱线图'),
        ('pie', '饼图'),
        ('correlation', '相关性矩阵'),
    )

    name = models.CharField(max_length=200, verbose_name="可视化名称")
    description = models.TextField(blank=True, verbose_name="描述")
    chart_type = models.CharField(max_length=50, choices=CHART_TYPES, verbose_name="图表类型")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, blank=True, verbose_name="关联数据集")
    training_session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, null=True, blank=True, verbose_name="关联训练会话")
    config = models.JSONField(verbose_name="可视化配置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")

    class Meta:
        verbose_name = "可视化配置"
        verbose_name_plural = verbose_name

class Dashboard(models.Model):
    """仪表板模型"""
    name = models.CharField(max_length=200, verbose_name="仪表板名称")
    description = models.TextField(blank=True, verbose_name="描述")
    layout = models.JSONField(verbose_name="布局配置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")
    visualizations = models.ManyToManyField(Visualization, through='DashboardItem', verbose_name="可视化组件")

    class Meta:
        verbose_name = "仪表板"
        verbose_name_plural = verbose_name

class DashboardItem(models.Model):
    """仪表板项目模型"""
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, verbose_name="所属仪表板")
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, verbose_name="可视化组件")
    position = models.JSONField(verbose_name="位置信息")
    size = models.JSONField(verbose_name="尺寸信息")
    order = models.IntegerField(verbose_name="显示顺序")

    class Meta:
        verbose_name = "仪表板项目"
        verbose_name_plural = verbose_name
        ordering = ['order'] 