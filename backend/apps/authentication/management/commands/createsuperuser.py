"""
Переопределение стандартной команды createsuperuser для работы с phone_number
"""
from django.contrib.auth.management.commands import createsuperuser as BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = User
        self.username_field = User._meta.get_field(User.USERNAME_FIELD)

    def get_input_data(self, field, message, default=None):
        """
        Переопределяем для использования phone_number вместо username
        """
        if field.name == 'phone_number':
            raw_value = input(message)
            return raw_value
        return super().get_input_data(field, message, default)

