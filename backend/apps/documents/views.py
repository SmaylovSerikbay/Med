"""
Document views
"""
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Document, DocumentSignature, CalendarPlan
from .serializers import (
    DocumentSerializer,
    DocumentSignatureSerializer,
    CalendarPlanSerializer
)
from .services import DocumentService


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet для документов"""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Показываем документы только организаций, где пользователь имеет доступ
        from apps.organizations.models import Organization, ClinicEmployerPartnership
        from django.db.models import Q
        
        # Работодатель: видит документы своих организаций
        employer_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user, members__role__in=['hr', 'admin', 'safety']),
            org_type='employer'
        ).values_list('id', flat=True)
        
        # Клиника: видит документы где они участвуют
        clinic_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user),
            org_type='clinic'
        ).values_list('id', flat=True)
        
        org_ids = list(employer_ids) + list(clinic_ids)
        
        # Базовый queryset - документы организаций пользователя
        queryset = Document.objects.filter(organization_id__in=org_ids)
        
        # Для клиники: показываем документы, связанные с партнерскими работодателями
        user_clinic = Organization.objects.filter(
            owner=user,
            org_type='clinic'
        ).first()
        
        if user_clinic:
            # Находим работодателей с активными партнерствами
            active_partnerships = ClinicEmployerPartnership.objects.filter(
                clinic=user_clinic,
                status=ClinicEmployerPartnership.PartnershipStatus.ACTIVE
            )
            partner_employer_ids = [p.employer_id for p in active_partnerships if p.is_active()]
            
            # Также проверяем документы через CalendarPlan - если клиника участвует в плане,
            # то она должна видеть документы календарного плана
            calendar_plan_doc_ids = []
            if partner_employer_ids:
                from .models import CalendarPlan
                calendar_plans = CalendarPlan.objects.filter(
                    clinic=user_clinic,
                    employer_id__in=partner_employer_ids
                )
                calendar_plan_doc_ids = [cp.document_id for cp in calendar_plans if cp.document_id]
            
            # Клиника видит:
            # 1. Документы своих организаций
            # 2. Документы, которые она создала
            # 3. Документы партнерских работодателей (Приложение 3, Календарный план, Заключительный акт)
            # 4. Документы календарных планов, где она участвует
            from functools import reduce
            import operator
            
            conditions = [
                Q(organization_id__in=org_ids),
                Q(created_by=user)
            ]
            
            if partner_employer_ids:
                conditions.append(Q(organization_id__in=partner_employer_ids))
            
            if calendar_plan_doc_ids:
                conditions.append(Q(id__in=calendar_plan_doc_ids))
            
            # Объединяем условия через OR
            if len(conditions) > 1:
                combined_condition = reduce(operator.or_, conditions)
                queryset = Document.objects.filter(combined_condition)
            else:
                queryset = Document.objects.filter(conditions[0])
            
            # Фильтруем документы календарного плана - показываем только те, у которых есть связанный CalendarPlan
            queryset = queryset.exclude(
                document_type='calendar_plan',
                calendar_plan__isnull=True
            )
        
        # Для работодателя: показываем также документы, созданные клиниками-партнерами
        if employer_ids:
            # Находим клиники с активными партнерствами
            active_partnerships = ClinicEmployerPartnership.objects.filter(
                employer_id__in=employer_ids,
                status=ClinicEmployerPartnership.PartnershipStatus.ACTIVE
            )
            partner_clinic_ids = [p.clinic_id for p in active_partnerships if p.is_active()]
            
            if partner_clinic_ids:
                # Находим клиники
                partner_clinics = Organization.objects.filter(id__in=partner_clinic_ids)
                # Находим пользователей этих клиник
                clinic_owners = [c.owner_id for c in partner_clinics if c.owner_id]
                
                if clinic_owners:
                    # Работодатель видит документы, созданные клиниками-партнерами для его организаций
                    queryset = queryset | Document.objects.filter(
                        Q(organization_id__in=employer_ids) |
                        Q(created_by_id__in=clinic_owners, organization_id__in=employer_ids)
                    )
                
                # Также добавляем документы календарных планов, где работодатель участвует
                from .models import CalendarPlan
                calendar_plans = CalendarPlan.objects.filter(employer_id__in=employer_ids)
                calendar_plan_doc_ids = [cp.document_id for cp in calendar_plans if cp.document_id]
                
                if calendar_plan_doc_ids:
                    queryset = queryset | Document.objects.filter(id__in=calendar_plan_doc_ids)
        
        # Фильтруем документы календарного плана - показываем только те, у которых есть связанный CalendarPlan
        # Это предотвращает показ документов, у которых CalendarPlan был удален
        queryset = queryset.exclude(
            document_type='calendar_plan',
            calendar_plan__isnull=True
        )
        
        return queryset.distinct().order_by('-created_at')
    
    @action(detail=False, methods=['get', 'post'])
    def get_or_generate_appendix_3(self, request):
        """
        Получить или автоматически сформировать Приложение 3
        
        GET: Получить существующее Приложение 3 (если есть) или автоматически сформировать
        POST: Принудительно обновить/сформировать Приложение 3
        
        АВТОМАТИЧЕСКИ формируется на основе уже добавленных сотрудников
        """
        employer_id = request.query_params.get('employer_id') or request.data.get('employer_id')
        year = request.query_params.get('year') or request.data.get('year', timezone.now().year)
        
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
        
        # Автоматически формируем или получаем Приложение 3
        document = DocumentService.generate_appendix_3(employer, int(year))
        
        serializer = self.get_serializer(document)
        response_data = serializer.data
        
        # Добавляем информацию о возможности создания календарного плана
        from apps.organizations.models import ClinicEmployerPartnership
        user_clinic = Organization.objects.filter(
            owner=request.user,
            org_type='clinic'
        ).first()
        
        if user_clinic:
            active_partnerships = ClinicEmployerPartnership.objects.filter(
                employer=employer,
                clinic=user_clinic,
                status=ClinicEmployerPartnership.PartnershipStatus.ACTIVE
            )
            if active_partnerships.exists() and active_partnerships.first().is_active():
                response_data['can_create_calendar_plan'] = True
                response_data['suggested_clinic_id'] = user_clinic.id
            else:
                response_data['can_create_calendar_plan'] = False
        else:
            response_data['can_create_calendar_plan'] = False
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def generate_appendix_3(self, request):
        """Генерация/обновление Приложения 3 (Список лиц) - только клиника
        
        АВТОМАТИЧЕСКИ формируется на основе уже добавленных сотрудников.
        Если документ уже существует - обновляется автоматически.
        """
        from apps.organizations.models import Organization
        from apps.subscriptions.services import SubscriptionService
        
        employer_id = request.data.get('employer_id')
        year = request.data.get('year', timezone.now().year)
        
        # Проверяем, что пользователь - владелец клиники
        user_clinic = Organization.objects.filter(
            owner=request.user,
            org_type='clinic'
        ).first()
        
        if not user_clinic:
            return Response(
                {'error': 'Только владельцы клиник могут генерировать документы'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем активную подписку клиники
        if not SubscriptionService.check_organization_access(user_clinic):
            return Response(
                {'error': 'Для генерации документов необходима активная подписка клиники'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            employer = Organization.objects.get(
                id=employer_id,
                org_type='employer'
            )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Работодатель не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        document = DocumentService.generate_appendix_3(employer, year)
        # Устанавливаем, что документ создан клиникой
        document.created_by = request.user
        document.save()
        
        # Возвращаем документ с информацией о возможности создания календарного плана
        serializer = self.get_serializer(document)
        response_data = serializer.data
        
        # Добавляем флаг, что можно создать календарный план автоматически
        available_clinics = document.content.get('available_clinics_for_calendar_plan', [])
        if available_clinics:
            # Если есть активное партнерство с клиникой пользователя, предлагаем автоматическое создание
            user_clinic_id = user_clinic.id
            has_partnership = any(c['id'] == user_clinic_id for c in available_clinics)
            response_data['can_create_calendar_plan'] = has_partnership
            response_data['suggested_clinic_id'] = user_clinic_id if has_partnership else None
        else:
            response_data['can_create_calendar_plan'] = False
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def generate_calendar_plan(self, request):
        """Генерация Календарного плана - только клиника"""
        from apps.organizations.models import Organization
        from apps.subscriptions.services import SubscriptionService
        
        employer_id = request.data.get('employer_id')
        clinic_id = request.data.get('clinic_id')
        year = request.data.get('year', timezone.now().year)
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        
        # Проверяем, что пользователь - владелец клиники
        user_clinic = Organization.objects.filter(
            owner=request.user,
            org_type='clinic'
        ).first()
        
        if not user_clinic:
            return Response(
                {'error': 'Только владельцы клиник могут генерировать документы'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем активную подписку клиники
        if not SubscriptionService.check_organization_access(user_clinic):
            return Response(
                {'error': 'Для генерации документов необходима активная подписка клиники'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            employer = Organization.objects.get(id=employer_id, org_type='employer')
            # Клиника генерирует документ от своего имени, clinic_id должен совпадать с клиникой пользователя
            if clinic_id and int(clinic_id) != user_clinic.id:
                return Response(
                    {'error': 'Вы можете генерировать документы только от имени своей клиники'},
                    status=status.HTTP_403_FORBIDDEN
                )
            clinic = user_clinic
            
            # Проверяем партнерство или публичность клиники
            from apps.organizations.models import ClinicEmployerPartnership
            partnership = ClinicEmployerPartnership.objects.filter(
                clinic=clinic,
                employer=employer
            ).first()
            
            if not partnership or not partnership.is_active():
                # Проверяем, не является ли клиника публичной
                if not partnership or not partnership.is_public:
                    return Response(
                        {'error': 'Необходимо активное партнерство с работодателем. Запросите партнерство или сделайте клинику публичной.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                start_date = timezone.now()
            
            end_date = None
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                # Проверяем, что end_date позже start_date
                if end_date <= start_date:
                    return Response(
                        {'error': 'Дата окончания должна быть позже даты начала'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': f'Неверный формат даты: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, существует ли уже план для этого работодателя и года
        existing_plan = CalendarPlan.objects.filter(
            employer=employer,
            year=year
        ).first()
        
        if existing_plan:
            # Если план уже существует, возвращаем его с сообщением
            serializer = CalendarPlanSerializer(existing_plan)
            return Response(
                {
                    'id': existing_plan.id,
                    'message': 'Календарный план уже существует для этого работодателя и года. Используйте редактирование для изменения.',
                    'plan': serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        try:
            calendar_plan = DocumentService.generate_calendar_plan(
                employer=employer,
                clinic=clinic,
                year=year,
                start_date=start_date,
                end_date=end_date
            )
            # Устанавливаем, что документ создан клиникой
            if calendar_plan.document:
                calendar_plan.document.created_by = request.user
                calendar_plan.document.save()
            serializer = CalendarPlanSerializer(calendar_plan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def generate_final_act(self, request):
        """Генерация Заключительного акта - только клиника"""
        from apps.organizations.models import Organization
        from apps.subscriptions.services import SubscriptionService
        
        employer_id = request.data.get('employer_id')
        clinic_id = request.data.get('clinic_id')
        year = request.data.get('year', timezone.now().year)
        
        # Проверяем, что пользователь - владелец клиники
        user_clinic = Organization.objects.filter(
            owner=request.user,
            org_type='clinic'
        ).first()
        
        if not user_clinic:
            return Response(
                {'error': 'Только владельцы клиник могут генерировать документы'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем активную подписку клиники
        if not SubscriptionService.check_organization_access(user_clinic):
            return Response(
                {'error': 'Для генерации документов необходима активная подписка клиники'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            employer = Organization.objects.get(id=employer_id, org_type='employer')
            # Клиника генерирует документ от своего имени, clinic_id должен совпадать с клиникой пользователя
            if clinic_id and int(clinic_id) != user_clinic.id:
                return Response(
                    {'error': 'Вы можете генерировать документы только от имени своей клиники'},
                    status=status.HTTP_403_FORBIDDEN
                )
            clinic = user_clinic
            
            # Проверяем партнерство или публичность клиники
            from apps.organizations.models import ClinicEmployerPartnership
            partnership = ClinicEmployerPartnership.objects.filter(
                clinic=clinic,
                employer=employer
            ).first()
            
            if not partnership or not partnership.is_active():
                if not partnership or not partnership.is_public:
                    return Response(
                        {'error': 'Необходимо активное партнерство с работодателем'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        document = DocumentService.generate_final_act(employer, clinic, year)
        # Устанавливаем, что документ создан клиникой
        document.created_by = request.user
        document.save()
        serializer = self.get_serializer(document)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def request_signature(self, request, pk=None):
        """Запросить подпись документа через OTP"""
        document = self.get_object()
        signer_role = request.data.get('role')
        
        if signer_role not in ['clinic', 'employer', 'ses']:
            return Response(
                {'error': 'Неверная роль подписанта'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            signature = DocumentService.request_signature(document, signer_role)
            return Response({
                'message': 'OTP код отправлен на WhatsApp',
                'signature_id': signature.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def verify_and_sign(self, request, pk=None):
        """Проверить OTP и подписать документ"""
        document = self.get_object()
        signer_role = request.data.get('role')
        otp_code = request.data.get('otp_code')
        
        if not otp_code:
            return Response(
                {'error': 'Укажите OTP код'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ip_address = request.META.get('REMOTE_ADDR', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            signature = DocumentService.verify_and_sign(
                document=document,
                signer_role=signer_role,
                otp_code=otp_code,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            serializer = DocumentSignatureSerializer(signature)
            return Response({
                'message': 'Документ успешно подписан',
                'signature': serializer.data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CalendarPlanViewSet(viewsets.ModelViewSet):
    """ViewSet для календарных планов"""
    serializer_class = CalendarPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        from apps.organizations.models import Organization
        from django.db.models import Q
        
        # Работодатель: видит планы своих организаций
        employer_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user, members__role__in=['hr', 'admin', 'safety']),
            org_type='employer'
        ).values_list('id', flat=True)
        
        # Клиника: видит планы работодателей, с которыми есть партнерство
        clinic_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user),
            org_type='clinic'
        ).values_list('id', flat=True)
        
        queryset = CalendarPlan.objects.none()
        
        # Для работодателя: показываем планы его организаций
        if employer_ids:
            queryset = queryset | CalendarPlan.objects.filter(employer_id__in=employer_ids)
        
        # Для клиники: показываем планы, где клиника является исполнителем
        if clinic_ids:
            queryset = queryset | CalendarPlan.objects.filter(clinic_id__in=clinic_ids)
        
        return queryset.distinct().order_by('-created_at')
    
    def update(self, request, *args, **kwargs):
        """Обновление календарного плана - только клиника"""
        instance = self.get_object()
        
        # Проверяем, что пользователь - владелец клиники или член клиники
        user_clinic = Organization.objects.filter(
            Q(owner=request.user) | Q(members__user=request.user),
            org_type='clinic',
            id=instance.clinic_id
        ).first()
        
        if not user_clinic:
            return Response(
                {'error': 'Только клиника, создавшая план, может его редактировать'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление календарного плана"""
        return self.update(request, *args, **kwargs)

