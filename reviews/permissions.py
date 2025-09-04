from django.conf import settings
from rest_framework import permissions

class HasAPIAccessToken(permissions.BasePermission):
    """
    Permission для проверки валидного токена доступа.
    Ожидает токен в заголовке Authorization: Token <token_here>
    """
    
    def has_permission(self, request, view):
        # Разрешаю все GET запросы (для просмотра)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Проверяю токен для изменяющих операций (POST, PUT, PATCH, DELETE)
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Token '):
            return False
            
        token = auth_header[6:].strip()  # Убираю 'Token ' из начала строки
        
        # Использую токен из настроек Django
        return token == settings.API_ACCESS_TOKEN