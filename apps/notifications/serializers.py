from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'level', 'read', 
                 'created_at', 'content_type', 'object_id']
        read_only_fields = ['created_at'] 