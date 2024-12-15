import json
import asyncio
import psutil
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import TrainingSession, TrainingLog
from django.utils import timezone

class TrainingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f'training_{self.session_id}'

        # 加入训练会话组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 离开训练会话组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """处理接收到的消息"""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'start_training':
            await self.start_training()
        elif message_type == 'stop_training':
            await self.stop_training()

    async def training_message(self, event):
        """发送训练相关消息到WebSocket"""
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_training_session(self):
        """获取训练会话"""
        return TrainingSession.objects.get(id=self.session_id)

    @database_sync_to_async
    def save_training_log(self, metrics):
        """保存训练日志"""
        session = TrainingSession.objects.get(id=self.session_id)
        TrainingLog.objects.create(
            session=session,
            epoch=metrics['epoch'],
            metrics=metrics
        )

    async def start_training(self):
        """开始训练过程"""
        session = await self.get_training_session()
        if session.status != 'running':
            return

        # 模拟训练过程
        for epoch in range(session.hyperparameters.get('epochs', 10)):
            if session.status != 'running':
                break

            # 模拟训练一个epoch
            metrics = {
                'epoch': epoch + 1,
                'loss': 0.5 - (epoch * 0.05),
                'accuracy': 0.6 + (epoch * 0.04),
                'val_loss': 0.6 - (epoch * 0.04),
                'val_accuracy': 0.55 + (epoch * 0.03)
            }

            # 保存���练日志
            await self.save_training_log(metrics)

            # 发送训练指标
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'training_message',
                    'data': {
                        'type': 'metrics',
                        'metrics': metrics
                    }
                }
            )

            # 模拟训练延迟
            await asyncio.sleep(1)

class SystemMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.should_send_updates = True
        asyncio.create_task(self.send_system_metrics())

    async def disconnect(self, close_code):
        self.should_send_updates = False

    async def send_system_metrics(self):
        """定期发送系统指标"""
        while self.should_send_updates:
            metrics = {
                'type': 'system_metrics',
                'data': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent
                }
            }
            await self.send(text_data=json.dumps(metrics))
            await asyncio.sleep(5)  # 每5秒更新一次 