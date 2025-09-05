from django.conf import settings
from rest_framework import permissions

class HasAPIAccessToken(permissions.BasePermission):
    """
    Permission для проверки валидного токена доступа.
    Простая проверка кастомного токена из настроек.
    """
    
    def has_permission(self, request, view):
        # Разрешаю все GET запросы (для просмотра)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Проверяю кастомный токен из заголовка
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Token '):
            return False
            
        token = auth_header[6:].strip()  # Убираю 'Token ' из начала строки
        
        # Использую токен из настроек Django
        expected_token = getattr(settings, 'API_ACCESS_TOKEN', None)
        
        if not expected_token:
            # Если токен не настроен, разрешаю все
            return True
            
        return token == expected_token
