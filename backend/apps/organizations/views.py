"""
Organization views
"""
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership
from .serializers import (
    OrganizationSerializer,
    OrganizationMemberSerializer,
    EmployeeSerializer,
    EmployeeCreateSerializer,
    ClinicEmployerPartnershipSerializer
)

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet для организаций"""
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Показываем организации, где пользователь владелец или участник
        from django.db.models import Q
        return Organization.objects.filter(
            Q(owner=user) | Q(members__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        # Автоматически устанавливаем владельца из текущего пользователя
        organization = serializer.save(owner=self.request.user)
        
        # НЕ создаем подписку автоматически
        # Пользователь должен будет запросить подписку отдельно через API
        # Подписка будет создана только при запросе через request_subscription
    
    @action(detail=False, methods=['get'])
    def my_organizations(self, request):
        """Мои организации"""
        user = request.user
        from django.db.models import Q
        organizations = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user)
        ).distinct()
        serializer = self.get_serializer(organizations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all_clinics(self, request):
        """Получить все клиники в системе (для запроса партнерства)"""
        # Получаем ВСЕ клиники без фильтрации по пользователю
        all_clinics = Organization.objects.filter(org_type='clinic')
        serializer = self.get_serializer(all_clinics, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Добавить участника в организацию (врача, регистратора и т.д.)"""
        organization = self.get_object()
        # Проверка прав
        if organization.owner != request.user:
            return Response(
                {'error': 'Только владелец может добавлять участников'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        phone_number = request.data.get('phone_number')
        role = request.data.get('role')
        specialization = request.data.get('specialization', '')
        license_number = request.data.get('license_number', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        middle_name = request.data.get('middle_name', '')
        
        if not phone_number or not role:
            return Response(
                {'error': 'Номер телефона и роль обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Нормализуем номер телефона
        from apps.authentication.services import OTPService
        normalized_phone = OTPService.normalize_phone(phone_number)
        
        # Создаем или получаем пользователя для участника
        user, created = User.objects.get_or_create(
            phone_number=normalized_phone,
            defaults={
                'username': normalized_phone,
                'phone_verified': False,  # Пока не подтвержден через OTP
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        # Обновляем данные пользователя (имя, фамилия) если они были переданы
        updated = False
        if first_name:
            user.first_name = first_name
            updated = True
        if last_name:
            user.last_name = last_name
            updated = True
        if middle_name:
            # Сохраняем отчество в email поле временно (можно добавить отдельное поле позже)
            user.email = middle_name
            updated = True
        if updated:
            user.save()
        
        # Если пользователь уже существовал, обновляем username если нужно
        if not created and not user.username:
            user.username = normalized_phone
            user.save()
        
        # Создаем участника организации
        member, created = OrganizationMember.objects.get_or_create(
            organization=organization,
            user=user,
            defaults={
                'role': role,
                'specialization': specialization,
                'license_number': license_number,
            }
        )
        
        # Если участник уже существовал, обновляем данные
        if not created:
            member.role = role
            member.specialization = specialization
            member.license_number = license_number
            member.is_active = True
            member.save()
        
        # Отправляем приветственное сообщение медработнику через WhatsApp
        try:
            from apps.authentication.services import GreenAPIService
            from django.conf import settings
            
            role_display = dict(OrganizationMember.ROLE_CHOICES).get(member.role, member.role)
            org_type_display = 'клинику' if organization.org_type == 'clinic' else 'организацию'
            site_url = getattr(settings, 'FRONTEND_URL', 'https://profmed.kz')
            
            welcome_message = (
                f"👋 Добро пожаловать в ProfMed.kz!\n\n"
                f"✅ Вы зарегистрированы в {org_type_display} '{organization.name}' как {role_display}.\n\n"
                f"📱 Ваш номер телефона для входа: {normalized_phone}\n"
                f"🔐 Вход осуществляется по OTP коду, который будет отправлен в WhatsApp при авторизации.\n\n"
                f"🌐 Откройте сайт: {site_url}\n"
                f"1. Введите ваш номер телефона\n"
                f"2. Получите код в WhatsApp\n"
                f"3. Введите код для входа\n\n"
                f"После входа вы сможете работать с осмотрами и пациентами."
            )
            GreenAPIService.send_whatsapp_message(normalized_phone, welcome_message)
        except Exception as e:
            # Не блокируем создание если не удалось отправить сообщение
            print(f"Не удалось отправить приветственное сообщение: {e}")
        
        serializer = OrganizationMemberSerializer(member)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Получить список участников организации"""
        organization = self.get_object()
        
        # Проверяем права - только владелец или участник может видеть список
        if organization.owner != request.user:
            from apps.organizations.models import OrganizationMember
            is_member = OrganizationMember.objects.filter(
                organization=organization,
                user=request.user,
                is_active=True
            ).exists()
            if not is_member:
                return Response(
                    {'error': 'Нет доступа к этой организации'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        members = organization.members.filter(is_active=True)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet для сотрудников"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Показываем только сотрудников организаций, где пользователь владелец или HR
        from django.db.models import Q
        
        # Получаем ID работодателей, где пользователь владелец или участник с ролью HR/Admin
        employer_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user, members__role__in=['hr', 'admin', 'safety']),
            org_type='employer'
        ).values_list('id', flat=True)
        
        return Employee.objects.filter(employer_id__in=employer_ids)
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Автоматически определяем работодателя из организаций пользователя
        from django.db.models import Q
        employer_orgs = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user, members__role__in=['hr', 'admin', 'safety']),
            org_type='employer'
        )
        
        if not employer_orgs.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('У вас нет доступа к организациям-работодателям')
        
        # Если не указан работодатель, берем первую организацию пользователя
        if 'employer' not in serializer.validated_data or not serializer.validated_data.get('employer'):
            serializer.validated_data['employer'] = employer_orgs.first()
        
        # Проверяем что указанный работодатель доступен пользователю
        employer = serializer.validated_data['employer']
        if employer not in employer_orgs:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('У вас нет доступа к этой организации')
        
        # Проверяем активную подписку организации
        from apps.subscriptions.services import SubscriptionService
        if not SubscriptionService.check_organization_access(employer):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Для добавления сотрудников необходима активная подписка организации. Запросите подписку в разделе "Подписки".')
        
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        """Импорт сотрудников из Excel"""
        # TODO: Реализовать парсинг Excel
        return Response({'message': 'Импорт Excel будет реализован'}, status=status.HTTP_501_NOT_IMPLEMENTED)


class ClinicEmployerPartnershipViewSet(viewsets.ModelViewSet):
    """ViewSet для партнерств клиник и работодателей"""
    serializer_class = ClinicEmployerPartnershipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        from django.db.models import Q
        
        # Работодатель видит свои партнерства
        employer_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user),
            org_type='employer'
        ).values_list('id', flat=True)
        
        # Клиника видит свои партнерства
        clinic_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user),
            org_type='clinic'
        ).values_list('id', flat=True)
        
        return ClinicEmployerPartnership.objects.filter(
            Q(employer_id__in=employer_ids) | Q(clinic_id__in=clinic_ids)
        ).distinct()
    
    @action(detail=False, methods=['post'])
    def request_partnership(self, request):
        """Запросить партнерство (работодатель)"""
        employer_id = request.data.get('employer_id')
        clinic_id = request.data.get('clinic_id')
        default_price = request.data.get('default_price', 0)
        
        try:
            employer = Organization.objects.get(id=employer_id, org_type='employer')
            clinic = Organization.objects.get(id=clinic_id, org_type='clinic')
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем, что пользователь - владелец работодателя
        if employer.owner != request.user:
            return Response(
                {'error': 'Только владелец организации может запрашивать партнерство'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем, нет ли уже партнерства
        partnership, created = ClinicEmployerPartnership.objects.get_or_create(
            clinic=clinic,
            employer=employer,
            defaults={
                'status': ClinicEmployerPartnership.PartnershipStatus.PENDING,
                'requested_by': request.user,
                'default_price': default_price,
            }
        )
        
        if not created:
            return Response(
                {'error': 'Партнерство уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Отправляем уведомление клинике
        from apps.authentication.services import GreenAPIService
        try:
            message = (
                f"Новый запрос на партнерство от {employer.name}\n\n"
                f"Работодатель: {employer.name}\n"
                f"Предлагаемая цена: {default_price} тенге\n\n"
                f"Войдите в систему для подтверждения."
            )
            GreenAPIService.send_whatsapp_message(clinic.owner.phone_number, message)
        except Exception:
            pass
        
        serializer = self.get_serializer(partnership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Подтвердить партнерство (клиника)"""
        partnership = self.get_object()
        
        # Проверяем, что пользователь - владелец клиники
        if partnership.clinic.owner != request.user:
            return Response(
                {'error': 'Только владелец клиники может подтверждать партнерство'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pricing = request.data.get('pricing', {})
        default_price = request.data.get('default_price', partnership.default_price)
        notes = request.data.get('notes', '')
        expires_at = request.data.get('expires_at')
        
        from django.utils import timezone
        partnership.status = ClinicEmployerPartnership.PartnershipStatus.ACTIVE
        partnership.confirmed_by = request.user
        partnership.confirmed_at = timezone.now()
        partnership.pricing = pricing
        partnership.default_price = default_price
        partnership.notes = notes
        if expires_at:
            from datetime import datetime
            partnership.expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        partnership.save()
        
        # Отправляем уведомление работодателю
        from apps.authentication.services import GreenAPIService
        try:
            message = (
                f"Партнерство с клиникой {partnership.clinic.name} подтверждено!\n\n"
                f"Цена: {default_price} тенге\n"
                f"Теперь вы можете назначать осмотры в этой клинике."
            )
            GreenAPIService.send_whatsapp_message(partnership.employer.owner.phone_number, message)
        except Exception:
            pass
        
        serializer = self.get_serializer(partnership)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Отклонить партнерство (клиника)"""
        partnership = self.get_object()
        
        if partnership.clinic.owner != request.user:
            return Response(
                {'error': 'Только владелец клиники может отклонять партнерство'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partnership.status = ClinicEmployerPartnership.PartnershipStatus.REJECTED
        partnership.save()
        
        serializer = self.get_serializer(partnership)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_clinics(self, request):
        """Получить список доступных клиник для работодателя
        
        Показывает все клиники, кроме тех, с которыми уже есть активное партнерство
        (чтобы избежать дублирования, но позволить запросить новое партнерство)
        """
        employer_id = request.query_params.get('employer_id')
        if not employer_id:
            return Response(
                {'error': 'Укажите employer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employer = Organization.objects.get(id=employer_id, org_type='employer')
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Работодатель не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Получаем ВСЕ клиники в системе (без фильтрации по пользователю)
        all_clinics = Organization.objects.filter(org_type='clinic')
        
        # Логируем для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Total clinics in database: {all_clinics.count()}")
        
        # Получаем ID клиник, с которыми уже есть активное/ожидающее партнерство
        existing_partnership_ids = list(ClinicEmployerPartnership.objects.filter(
            employer=employer,
            status__in=[
                ClinicEmployerPartnership.PartnershipStatus.ACTIVE,
                ClinicEmployerPartnership.PartnershipStatus.PENDING
            ]
        ).values_list('clinic_id', flat=True))
        
        logger.info(f"Existing partnerships for employer {employer_id}: {len(existing_partnership_ids)} partnerships")
        
        # Показываем все клиники, кроме тех, с которыми уже есть активное/ожидающее партнерство
        if existing_partnership_ids:
            available_clinics = all_clinics.exclude(id__in=existing_partnership_ids)
        else:
            # Если нет существующих партнерств, показываем все клиники
            available_clinics = all_clinics
        
        logger.info(f"Available clinics for employer {employer_id}: {available_clinics.count()} clinics found")
        
        # Сериализуем клиники
        clinic_serializer = OrganizationSerializer(available_clinics, many=True)
        serialized_data = clinic_serializer.data
        
        logger.info(f"Serialized {len(serialized_data)} clinics")
        
        return Response(serialized_data)
    
    @action(detail=False, methods=['get'])
    def partner_employers(self, request):
        """Получить список работодателей с активными партнерствами для клиники пользователя
        
        Используется клиникой для выбора работодателя при генерации документов
        """
        from apps.organizations.models import Organization, ClinicEmployerPartnership
        from apps.organizations.serializers import OrganizationSerializer
        
        # Проверяем, что пользователь - владелец клиники
        user_clinic = Organization.objects.filter(
            owner=request.user,
            org_type='clinic'
        ).first()
        
        if not user_clinic:
            return Response(
                {'error': 'Только владельцы клиник могут просматривать партнеров'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Получаем работодателей с активными партнерствами
        active_partnerships = ClinicEmployerPartnership.objects.filter(
            clinic=user_clinic,
            status=ClinicEmployerPartnership.PartnershipStatus.ACTIVE
        ).select_related('employer')
        
        # Проверяем, что партнерство не истекло
        employers = []
        for partnership in active_partnerships:
            if partnership.is_active():
                employers.append(partnership.employer)
        
        # Сериализуем работодателей
        serializer = OrganizationSerializer(employers, many=True)
        return Response(serializer.data)

