from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import IntegrityError
import logging
from rest_framework_simplejwt.tokens import RefreshToken

# 添加日志记录
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        # 添加请求数据日志
        logger.info(f"收到注册请求: {request.data}")
        
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # 详细的参数验证
        if not username:
            return Response(
                {'message': '用户名不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not email:
            return Response(
                {'message': '邮箱不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not password:
            return Response(
                {'message': '密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 用户名长度验证
        if len(username) < 3:
            return Response(
                {'message': '用户名长度不能小于3个字符'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 密码长度验证
        if len(password) < 6:
            return Response(
                {'message': '密码长度不���小于6个字符'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return Response(
                {'message': '用户名已存在'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 检查邮箱是否已存在
        if User.objects.filter(email=email).exists():
            return Response(
                {'message': '邮箱已被注册'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 创建新用户
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # 生成Token
        refresh = RefreshToken.for_user(user)
        
        # 添加成功日志
        logger.info(f"用户注册成功: {username}")
        
        return Response({
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
        
    except IntegrityError as e:
        logger.error(f"注册时发生完整性错误: {str(e)}")
        return Response(
            {'message': '注册失败，数据库错误'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"注册时发生未知错误: {str(e)}")
        return Response(
            {'message': f'注册失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not all([username, password]):
        return Response(
            {'message': '请输入用户名和密码'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })
    else:
        return Response(
            {'message': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': '已退出登录'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def settings_view(request):
    user = request.user
    email = request.data.get('email')
    old_password = request.data.get('oldPassword')
    new_password = request.data.get('newPassword')
    
    try:
        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                return Response(
                    {'message': '邮箱已被使用'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = email
        
        if old_password and new_password:
            if not user.check_password(old_password):
                return Response(
                    {'message': '旧密码错误'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(new_password)
        
        user.save()
        
        return Response({
            'message': '设置更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        return Response(
            {'message': f'设置更新失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 

@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    return Response({'message': 'CSRF cookie set'})