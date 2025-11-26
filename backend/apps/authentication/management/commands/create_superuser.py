"""
Кастомная команда для создания суперпользователя с номером телефона
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает суперпользователя с номером телефона'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone-number',
            type=str,
            help='Номер телефона суперпользователя',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Пароль суперпользователя',
        )

    def handle(self, *args, **options):
        phone_number = options.get('phone_number')
        password = options.get('password')

        if not phone_number:
            phone_number = input('Номер телефона: ')

        if User.objects.filter(phone_number=phone_number).exists():
            self.stdout.write(
                self.style.ERROR(f'Пользователь с номером {phone_number} уже существует')
            )
            return

        if not password:
            password = getpass.getpass('Пароль: ')
            password_confirm = getpass.getpass('Пароль (повторно): ')
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Пароли не совпадают'))
                return

        User.objects.create_superuser(
            phone_number=phone_number,
            password=password,
            phone_verified=True
        )

        self.stdout.write(
            self.style.SUCCESS(f'Суперпользователь {phone_number} успешно создан!')
        )

