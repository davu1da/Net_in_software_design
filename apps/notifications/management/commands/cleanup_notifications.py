from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = '清理旧的通知'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='要保留的通知天数（默认30天）'
        )
        parser.add_argument(
            '--read-only',
            action='store_true',
            help='仅清理已读通知'
        )

    def handle(self, *args, **options):
        days = options['days']
        read_only = options['read_only']
        cutoff_date = timezone.now() - timedelta(days=days)

        # 构建查询条件
        query = {'created_at__lt': cutoff_date}
        if read_only:
            query['read'] = True

        # 获取要删除的通知数量
        count = Notification.objects.filter(**query).count()

        # 执行删除
        Notification.objects.filter(**query).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'成功清理 {count} 条通知（{days}天前{"的已读" if read_only else "的所有"}通知）'
            )
        ) 