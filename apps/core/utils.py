from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is None:
        logger.error(f"未处理的异常: {str(exc)}")
        return Response({
            'message': '服务器内部错误'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response 