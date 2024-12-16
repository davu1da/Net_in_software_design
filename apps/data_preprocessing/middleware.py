from django.http import JsonResponse
from django.conf import settings

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path.startswith('/api/auth/'):
            return JsonResponse({'message': '请先登录'}, status=401)
        return self.get_response(request) 