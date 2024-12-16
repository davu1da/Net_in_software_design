# Generated by Django 5.1.4 on 2024-12-16 08:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='数据集名称')),
                ('description', models.TextField(blank=True, verbose_name='数据集描述')),
                ('file', models.FileField(upload_to='datasets/', verbose_name='数据文件')),
                ('file_type', models.CharField(choices=[('csv', 'CSV文件'), ('excel', 'Excel文件'), ('json', 'JSON文件')], max_length=20, verbose_name='文件类型')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('columns', models.JSONField(default=list, verbose_name='列信息')),
                ('row_count', models.IntegerField(default=0, verbose_name='行数')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='所有者')),
            ],
            options={
                'verbose_name': '数据集',
                'verbose_name_plural': '数据集',
            },
        ),
        migrations.CreateModel(
            name='PreprocessingStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='步骤名称')),
                ('step_type', models.CharField(choices=[('clean', '数据清洗'), ('transform', '数据转换'), ('encode', '编码转换'), ('scale', '数据缩放'), ('split', '数据分割')], max_length=20, verbose_name='步骤类型')),
                ('parameters', models.JSONField(verbose_name='步骤参数')),
                ('order', models.IntegerField(verbose_name='执行顺序')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', '待执行'), ('running', '执行中'), ('completed', '已完成'), ('failed', '失败')], default='pending', max_length=20)),
                ('result', models.JSONField(blank=True, null=True, verbose_name='执行结果')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preprocessing_steps', to='data_preprocessing.dataset')),
            ],
            options={
                'verbose_name': '预处理步骤',
                'verbose_name_plural': '预处理步骤',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PreprocessingTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='模板名称')),
                ('description', models.TextField(blank=True, verbose_name='模板描述')),
                ('steps', models.JSONField(verbose_name='预处理步骤')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_public', models.BooleanField(default=False, verbose_name='是否公开')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='所有者')),
            ],
            options={
                'verbose_name': '预处理模板',
                'verbose_name_plural': '预处理模板',
            },
        ),
        migrations.CreateModel(
            name='ProcessedDataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='��理后数据集名称')),
                ('file', models.FileField(upload_to='processed_datasets/', verbose_name='处理后文件')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('columns', models.JSONField(default=list, verbose_name='处理后列信息')),
                ('row_count', models.IntegerField(default=0, verbose_name='处理后行数')),
                ('original_dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processed_versions', to='data_preprocessing.dataset')),
                ('preprocessing_steps', models.ManyToManyField(related_name='resulting_datasets', to='data_preprocessing.preprocessingstep')),
            ],
            options={
                'verbose_name': '处理后数据集',
                'verbose_name_plural': '处理后数据集',
            },
        ),
    ]