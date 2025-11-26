"""
Authentication views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.authentication.services import GreenAPIService, OTPService
from apps.authentication.models import OTPCode
from apps.organizations.models import Organization, OrganizationMember, Employee

User = get_user_model()


def normalize_phone_number(phone: str) -> str:
    """Нормализация номера телефона"""
    return OTPService.normalize_phone(phone)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """Отправка OTP кода через WhatsApp"""
    phone_number = request.data.get('phone_number', '').strip()
    
    if not phone_number:
        return Response(
            {'error': 'Номер телефона обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    normalized_phone = normalize_phone_number(phone_number)
    
    # Генерируем и сохраняем OTP
    otp_code = OTPService.create_otp(normalized_phone)
    
    # Отправляем через Green-API
    message = f"Ваш код для входа в ProfMed.kz: {otp_code.code}\nКод действителен {settings.OTP_EXPIRY_MINUTES} минут."
    
    try:
        GreenAPIService.send_whatsapp_message(normalized_phone, message)
        return Response({
            'message': 'OTP код отправлен на WhatsApp',
            'phone_number': normalized_phone
        })
    except Exception as e:
        return Response(
            {'error': f'Ошибка отправки сообщения: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Проверка OTP кода и выдача токенов"""
    phone_number = request.data.get('phone_number', '').strip()
    code = request.data.get('code', '').strip()
    
    if not phone_number or not code:
        return Response(
            {'error': 'Номер телефона и код обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    normalized_phone = normalize_phone_number(phone_number)
    
    # Проверяем OTP
    is_valid, otp_obj = OTPService.validate_otp(normalized_phone, code)
    
    if not is_valid:
        return Response(
            {'error': 'Неверный или истекший код'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Создаем или получаем пользователя
    user, created = User.objects.get_or_create(
        phone_number=normalized_phone,
        defaults={
            'phone_verified': True,
            'username': normalized_phone,
        }
    )
    
    if not created:
        user.phone_verified = True
        user.save()
    
    # Генерируем токены
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': {
            'id': user.id,
            'phone_number': user.phone_number,
            'phone_verified': user.phone_verified,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        },
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_password(request):
    """Вход по номеру телефона и паролю"""
    phone_number = request.data.get('phone_number', '').strip()
    password = request.data.get('password', '')
    
    if not phone_number or not password:
        return Response(
            {'error': 'Номер телефона и пароль обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    normalized_phone = normalize_phone_number(phone_number)
    
    try:
        user = User.objects.get(phone_number=normalized_phone)
    except User.DoesNotExist:
        return Response(
            {'error': 'Неверный номер телефона или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Проверяем пароль
    if not user.check_password(password):
        return Response(
            {'error': 'Неверный номер телефона или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Генерируем токены
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': {
            'id': user.id,
            'phone_number': user.phone_number,
            'phone_verified': user.phone_verified,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        },
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_password(request):
    """Установить или изменить пароль"""
    new_password = request.data.get('new_password', '')
    current_password = request.data.get('current_password', '')
    
    if not new_password:
        return Response(
            {'error': 'Новый пароль обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 6:
        return Response(
            {'error': 'Пароль должен содержать минимум 6 символов'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    
    # Если у пользователя уже есть пароль, требуем текущий пароль
    if user.has_usable_password():
        if not current_password:
            return Response(
                {'error': 'Текущий пароль обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user.check_password(current_password):
            return Response(
                {'error': 'Неверный текущий пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # Устанавливаем новый пароль
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Пароль успешно установлен',
        'has_password': True
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_request(request):
    """Запрос на сброс пароля через WhatsApp OTP"""
    phone_number = request.data.get('phone_number', '').strip()
    
    if not phone_number:
        return Response(
            {'error': 'Номер телефона обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    normalized_phone = normalize_phone_number(phone_number)
    
    # Проверяем существование пользователя
    try:
        user = User.objects.get(phone_number=normalized_phone)
    except User.DoesNotExist:
        # Не раскрываем информацию о существовании пользователя
        return Response({
            'message': 'Если пользователь существует, код отправлен на WhatsApp',
            'phone_number': normalized_phone
        })
    
    # Генерируем и сохраняем OTP
    otp_code = OTPService.create_otp(normalized_phone)
    
    # Отправляем через Green-API
    message = f"Код для сброса пароля ProfMed.kz: {otp_code.code}\nКод действителен {settings.OTP_EXPIRY_MINUTES} минут."
    
    try:
        GreenAPIService.send_whatsapp_message(normalized_phone, message)
        return Response({
            'message': 'Код для сброса пароля отправлен на WhatsApp',
            'phone_number': normalized_phone
        })
    except Exception as e:
        return Response(
            {'error': f'Ошибка отправки сообщения: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """Подтверждение сброса пароля с OTP кодом"""
    phone_number = request.data.get('phone_number', '').strip()
    code = request.data.get('code', '').strip()
    new_password = request.data.get('new_password', '')
    
    if not phone_number or not code or not new_password:
        return Response(
            {'error': 'Номер телефона, код и новый пароль обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 6:
        return Response(
            {'error': 'Пароль должен содержать минимум 6 символов'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    normalized_phone = normalize_phone_number(phone_number)
    
    # Проверяем OTP
    is_valid, otp_obj = OTPService.validate_otp(normalized_phone, code)
    
    if not is_valid:
        return Response(
            {'error': 'Неверный или истекший код'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Получаем пользователя
    try:
        user = User.objects.get(phone_number=normalized_phone)
    except User.DoesNotExist:
        return Response(
            {'error': 'Пользователь не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Устанавливаем новый пароль
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Пароль успешно изменен'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Получить профиль пользователя с ролями"""
    user = request.user
    
    # Определяем роли пользователя
    roles = []
    organizations = []
    
    # Проверяем владение организациями
    owned_orgs = Organization.objects.filter(owner=user)
    for org in owned_orgs:
        if org.org_type == 'employer':
            roles.append('employer_owner')
        elif org.org_type == 'clinic':
            roles.append('clinic_owner')
        organizations.append({
            'id': org.id,
            'name': org.name,
            'type': org.org_type,
            'role': 'owner',
        })
    
    # Проверяем членство в организациях
    memberships = OrganizationMember.objects.filter(user=user, is_active=True).select_related('organization')
    for membership in memberships:
        if membership.organization.org_type == 'employer':
            if membership.role in ['hr', 'admin', 'safety']:
                roles.append('employer_staff')
        elif membership.organization.org_type == 'clinic':
            if membership.role in ['doctor', 'registrar', 'profpathologist']:
                roles.append('clinic_staff')
        
        organizations.append({
            'id': membership.organization.id,
            'name': membership.organization.name,
            'type': membership.organization.org_type,
            'role': membership.role,
            'specialization': membership.specialization,
            'license_number': membership.license_number,
        })
    
    # Проверяем является ли пользователь пациентом (Employee)
    employee = Employee.objects.filter(user=user, is_active=True).select_related('employer', 'position').first()
    employee_data = None
    if employee:
        roles.append('patient')
        employee_data = {
            'id': employee.id,
            'employer_id': employee.employer.id,
            'employer_name': employee.employer.name,
            'first_name': employee.first_name or '',
            'last_name': employee.last_name or '',
            'middle_name': employee.middle_name or '',
            'iin': employee.iin or '',
            'position_id': employee.position.id if employee.position else None,
            'position_name': employee.position.name if employee.position else None,
            'department': employee.department or '',
            'hire_date': employee.hire_date.isoformat() if employee.hire_date else None,
        }
    
    # Определяем основную роль для дашборда
    primary_role = 'patient'  # По умолчанию
    if 'employer_owner' in roles or 'employer_staff' in roles:
        primary_role = 'employer'
    elif 'clinic_owner' in roles or 'clinic_staff' in roles:
        primary_role = 'clinic'
    
    # Получаем данные медработника из первого членства в клинике
    medical_staff_data = None
    clinic_membership = memberships.filter(organization__org_type='clinic').first()
    if clinic_membership:
        medical_staff_data = {
            'organization_id': clinic_membership.organization.id,
            'organization_name': clinic_membership.organization.name,
            'role': clinic_membership.role,
            'specialization': clinic_membership.specialization or '',
            'license_number': clinic_membership.license_number or '',
        }
    
    return Response({
        'user': {
            'id': user.id,
            'phone_number': user.phone_number,
            'phone_verified': user.phone_verified,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'first_name': getattr(user, 'first_name', '') or '',
            'last_name': getattr(user, 'last_name', '') or '',
            'middle_name': getattr(user, 'middle_name', '') or '',
            'has_password': user.has_usable_password(),
        },
        'roles': roles,
        'primary_role': primary_role,
        'organizations': organizations,
        'employee': employee_data,
        'medical_staff': medical_staff_data,
    })
