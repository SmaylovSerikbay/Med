"""
Organization serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership
from apps.compliance.models import Profession

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'bin', 'address', 'phone', 'email',
            'capacity_per_day', 'created_at'
        ]
        read_only_fields = ['created_at']


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'organization', 'user', 'role', 'specialization',
            'license_number', 'is_active', 'user_phone', 'organization_name'
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    harmful_factors = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'employer', 'first_name', 'last_name', 'middle_name',
            'iin', 'position', 'department', 'hire_date', 'is_active',
            'employer_name', 'position_name', 'phone_number', 'harmful_factors',
            'full_name', 'created_at'
        ]
        read_only_fields = ['created_at', 'full_name']
    
    def get_harmful_factors(self, obj):
        return [
            {'id': f.id, 'code': f.code, 'name': f.name}
            for f in obj.position.harmful_factors.filter(is_active=True)
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    employer = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(org_type='employer'),
        required=False,  # Не обязателен, будет определен автоматически
        allow_null=True
    )
    
    class Meta:
        model = Employee
        fields = [
            'phone_number', 'employer', 'first_name', 'last_name', 'middle_name',
            'iin', 'position', 'department', 'hire_date', 'position_start_date',
            'date_of_birth', 'gender', 'notes'
        ]
        extra_kwargs = {
            'position': {'required': False, 'allow_null': True},
        }
    
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        
        # Нормализуем номер телефона
        from apps.authentication.services import OTPService, GreenAPIService
        from django.conf import settings
        
        normalized_phone = OTPService.normalize_phone(phone_number)
        
        # Создаем или получаем пользователя для сотрудника
        user, created = User.objects.get_or_create(
            phone_number=normalized_phone,
            defaults={
                'username': normalized_phone,
                'phone_verified': False,  # Пока не подтвержден через OTP
            }
        )
        
        # Если пользователь уже существовал, обновляем username если нужно
        if not created and not user.username:
            user.username = normalized_phone
            user.save()
        
        validated_data['user'] = user
        employee = super().create(validated_data)
        
        # Отправляем приветственное сообщение сотруднику через WhatsApp
        try:
            employer = validated_data.get('employer')
            site_url = getattr(settings, 'FRONTEND_URL', 'https://profmed.kz')
            
            welcome_message = (
                f"👋 Добро пожаловать в ProfMed.kz!\n\n"
                f"✅ Вы зарегистрированы как сотрудник в организации '{employer.name}'.\n\n"
                f"📱 Ваш номер телефона для входа: {normalized_phone}\n"
                f"🔐 Вход осуществляется по OTP коду, который будет отправлен в WhatsApp при авторизации.\n\n"
                f"🌐 Откройте сайт: {site_url}\n"
                f"1. Введите ваш номер телефона\n"
                f"2. Получите код в WhatsApp\n"
                f"3. Введите код для входа\n\n"
                f"После входа вы сможете просматривать свои медицинские осмотры и результаты."
            )
            GreenAPIService.send_whatsapp_message(normalized_phone, welcome_message)
        except Exception as e:
            # Не блокируем создание если не удалось отправить сообщение
            print(f"Не удалось отправить приветственное сообщение сотруднику: {e}")
        
        return employee


class ClinicEmployerPartnershipSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    employer_name = serializers.CharField(source='employer.name', read_only=True)
    requested_by_phone = serializers.CharField(source='requested_by.phone_number', read_only=True)
    confirmed_by_phone = serializers.CharField(source='confirmed_by.phone_number', read_only=True, allow_null=True)
    
    class Meta:
        model = ClinicEmployerPartnership
        fields = [
            'id', 'clinic', 'employer', 'status', 'pricing', 'default_price',
            'is_public', 'requested_by', 'confirmed_by', 'notes',
            'requested_at', 'confirmed_at', 'expires_at',
            'clinic_name', 'employer_name', 'requested_by_phone', 'confirmed_by_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['requested_at', 'confirmed_at', 'created_at', 'updated_at']

