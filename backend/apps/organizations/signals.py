"""
Signals for automatic document updates
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Employee
from apps.documents.services import DocumentService
from django.utils import timezone


@receiver(post_save, sender=Employee)
@receiver(post_delete, sender=Employee)
def auto_update_appendix_3(sender, instance, **kwargs):
    """
    Автоматически обновляет Приложение 3 при изменении сотрудников
    
    Вызывается при:
    - Создании нового сотрудника
    - Обновлении существующего сотрудника
    - Удалении сотрудника
    """
    if not instance.employer:
        return
    
    # Обновляем Приложение 3 для текущего года
    current_year = timezone.now().year
    
    try:
        DocumentService.generate_appendix_3(instance.employer, current_year)
    except Exception as e:
        # Логируем ошибку, но не блокируем сохранение сотрудника
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка автоматического обновления Приложения 3: {e}")

