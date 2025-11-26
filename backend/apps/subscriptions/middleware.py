"""
Middleware для проверки подписки организации
"""
from django.http import JsonResponse
from django.utils import timezone
from .models import Subscription
from .services import SubscriptionService


class SubscriptionMiddleware:
    """Middleware для проверки активной подписки организации"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Пропускаем админку и публичные эндпоинты
        if request.path.startswith('/admin/') or request.path.startswith('/api/auth/'):
            return self.get_response(request)
        
        # Проверяем только авторизованных пользователей
        if request.user.is_authenticated:
            # Получаем организации пользователя с активными подписками
            orgs_with_access = SubscriptionService.get_user_organizations_with_access(request.user)
            
            # Если у пользователя нет организаций с активными подписками
            if not orgs_with_access:
                # Разрешаем доступ к:
                # - Просмотру профиля
                # - Запросу подписки
                # - Созданию и просмотру организаций (чтобы можно было создать и запросить подписку)
                # - Просмотру планов подписки
                allowed_paths = [
                    '/api/auth/profile',
                    '/api/subscriptions/subscriptions/request_subscription',
                    '/api/subscriptions/plans/',
                    '/api/subscriptions/subscriptions/my_subscriptions/',
                    '/api/subscriptions/subscriptions/current/',
                    '/api/organizations/organizations/',  # Просмотр и создание организаций
                ]
                
                # Проверяем разрешенные пути
                if any(request.path.startswith(path) for path in allowed_paths):
                    return self.get_response(request)
                
                # Для остальных эндпоинтов требуем подписку
                # Но для некоторых эндпоинтов даем более понятное сообщение
                error_message = 'Для доступа к платформе необходима активная подписка организации. Запросите подписку в разделе "Подписки".'
                
                if '/employees/' in request.path:
                    error_message = 'Для добавления сотрудников необходима активная подписка организации. Запросите подписку в разделе "Подписки".'
                elif '/examinations/' in request.path:
                    error_message = 'Для создания медицинских осмотров необходима активная подписка организации. Запросите подписку в разделе "Подписки".'
                elif '/documents/' in request.path:
                    error_message = 'Для генерации документов необходима активная подписка организации. Запросите подписку в разделе "Подписки".'
                
                return JsonResponse(
                    {
                        'error': 'Требуется активная подписка',
                        'message': error_message
                    },
                    status=403
                )
        
        return self.get_response(request)
