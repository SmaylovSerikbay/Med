"""
Document services - Генерация документов согласно Приказу 131
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count
from .models import Document, DocumentType, DocumentSignature, CalendarPlan
from apps.organizations.models import Organization, Employee
from apps.medical_examinations.models import MedicalExamination, ExaminationResult
from apps.authentication.services import OTPService


class DocumentService:
    """Сервис для генерации документов"""
    
    @staticmethod
    def generate_appendix_3(employer: Organization, year: int) -> Document:
        """
        Генерация Приложения 3 - Список лиц, подлежащих осмотру
        
        Согласно Пункту 20.1 Приказа 131
        
        АВТОМАТИЧЕСКИ формируется на основе уже добавленных сотрудников:
        - Берет всех активных сотрудников работодателя
        - Автоматически определяет, кому нужен осмотр (на основе вредных факторов, периодичности, даты последнего осмотра)
        - Формирует официальный документ
        
        Примечание: Сотрудники должны быть заранее добавлены в систему
        (вручную или через импорт Excel - Форма 3 для массового импорта)
        """
        # Получаем всех активных сотрудников работодателя
        employees = Employee.objects.filter(
            employer=employer,
            is_active=True
        )
        
        # АВТОМАТИЧЕСКИ формируем список сотрудников, которым нужен осмотр
        employees_list = []
        for employee in employees:
            if not employee.position:
                # Если нет должности, не включаем (нужна должность для определения факторов)
                continue
            
            # Проверяем, нужен ли осмотр (по периодичности факторов)
            factors = employee.position.harmful_factors.filter(is_active=True)
            needs_examination = False
            
            # Если нет факторов - не включаем (или можно включить для общего осмотра)
            if factors.count() == 0:
                continue
            
            for factor in factors:
                # Проверяем последний осмотр через DoctorExamination
                from apps.medical_examinations.models import DoctorExamination
                
                last_doctor_exam = DoctorExamination.objects.filter(
                    examination__employee=employee,
                    examination__status='completed',
                    harmful_factor=factor
                ).select_related('examination').order_by('-examination__completed_date').first()
                
                if not last_doctor_exam or not last_doctor_exam.examination.completed_date:
                    needs_examination = True
                    break
                else:
                    # Проверяем периодичность
                    months_passed = (timezone.now().date() - last_doctor_exam.examination.completed_date.date()).days // 30
                    if months_passed >= factor.periodicity_months:
                        needs_examination = True
                        break
            
            # Также проверяем: если нет ни одного завершенного периодического осмотра за этот год
            if not needs_examination:
                from datetime import datetime as dt
                year_start = timezone.make_aware(dt(year, 1, 1))
                year_exams = MedicalExamination.objects.filter(
                    employee=employee,
                    examination_type='periodic',
                    status='completed',
                    completed_date__gte=year_start
                ).count()
                if year_exams == 0:
                        needs_examination = True
            
            if needs_examination:
                # Получаем полную информацию о сотруднике для таблицы (как в Excel форме)
                # Получаем дату рождения из User (если есть) или вычисляем из ИИН
                date_of_birth = None
                if employee.iin and len(employee.iin) >= 6:
                    # ИИН содержит дату рождения в формате YYMMDD
                    try:
                        year_prefix = '19' if int(employee.iin[0]) >= 5 else '20'
                        birth_year = int(year_prefix + employee.iin[0:2])
                        birth_month = int(employee.iin[2:4])
                        birth_day = int(employee.iin[4:6])
                        from datetime import date
                        date_of_birth = date(birth_year, birth_month, birth_day).isoformat()
                    except:
                        pass
                
                # Получаем пол из ИИН (7-я цифра: четная = женский, нечетная = мужской)
                gender = None
                if employee.iin and len(employee.iin) >= 7:
                    gender_digit = int(employee.iin[6])
                    gender = 'Женский' if gender_digit % 2 == 0 else 'Мужской'
                
                # Получаем вредные факторы
                harmful_factors_list = [f.name for f in factors]
                harmful_factors = ', '.join(harmful_factors_list) if harmful_factors_list else '-'
                
                # Получаем дату последнего осмотра
                last_exam = MedicalExamination.objects.filter(
                    employee=employee,
                    status='completed'
                ).order_by('-completed_date').first()
                last_examination_date = last_exam.completed_date.isoformat() if last_exam and last_exam.completed_date else None
                
                # Вычисляем стаж
                from datetime import date
                total_experience = None
                position_experience = None
                if employee.hire_date:
                    today = date.today()
                    total_days = (today - employee.hire_date).days
                    total_years = total_days // 365
                    total_months = (total_days % 365) // 30
                    total_experience = f"{total_years} л. {total_months} м." if total_years > 0 else f"{total_months} м."
                    
                    # Стаж по должности (пока используем общий стаж)
                    # TODO: можно добавить поле position_start_date в модель Employee
                    position_experience = total_experience
                
                employees_list.append({
                    'id': employee.id,
                    'full_name': employee.full_name,
                    'date_of_birth': date_of_birth,
                    'gender': gender,
                    'department': employee.department or '-',
                    'position': employee.position.name if employee.position else 'Не указана',
                    'total_experience': total_experience or '-',
                    'position_experience': position_experience or '-',
                    'last_examination_date': last_examination_date,
                    'harmful_factors': harmful_factors,
                    'notes': employee.notes or '',  # Примечание из модели Employee
                    'iin': employee.iin,
                })
        
        # Проверяем, существует ли уже Приложение 3 на этот год
        # Если существует - обновляем, если нет - создаем
        document, created = Document.objects.get_or_create(
            document_type=DocumentType.APPENDIX_3,
            organization=employer,
            year=year,
            defaults={
                'title': f"Список лиц, подлежащих обязательному медицинскому осмотру на {year} год",
                'content': {
                    'employees': employees_list,
                    'total_count': len(employees_list),
                    'generated_at': timezone.now().isoformat(),
                }
            }
        )
        
        # Если документ уже существовал, обновляем его
        if not created:
            document.title = f"Список лиц, подлежащих обязательному медицинскому осмотру на {year} год"
            document.content = {
                'employees': employees_list,
                'total_count': len(employees_list),
                'generated_at': timezone.now().isoformat(),
            }
            document.save()
        
        # Автоматически предлагаем создать календарный план, если есть активное партнерство
        # Это соответствует логике Приказа 131 - календарный план создается клиникой на основе Приложения 3
        from apps.organizations.models import ClinicEmployerPartnership
        active_partnerships = ClinicEmployerPartnership.objects.filter(
            employer=employer,
            status='active'
        ).select_related('clinic')
        
        # Добавляем информацию о доступных клиниках в метаданные документа
        available_clinics = [
            {
                'id': p.clinic.id,
                'name': p.clinic.name,
                'partnership_id': p.id
            }
            for p in active_partnerships if p.is_active()
        ]
        
        # Обновляем content с информацией о доступных клиниках
        content = document.content
        content['available_clinics_for_calendar_plan'] = available_clinics
        document.content = content
        document.save(update_fields=['content'])
        
        return document
    
    @staticmethod
    def generate_calendar_plan(
        employer: Organization,
        clinic: Organization,
        year: int,
        start_date: datetime,
        end_date: datetime = None
    ) -> CalendarPlan:
        """
        Генерация Календарного плана проведения осмотров
        
        Согласно Пункту 20.2 Приказа 131
        
        АВТОМАТИЧЕСКИ распределяет сотрудников из Приложения 3 по датам:
        - Берет список сотрудников из уже созданного Приложения 3
        - Автоматически распределяет их по датам с учетом пропускной способности клиники
        - Создает график осмотров (календарь)
        """
        # Получаем список сотрудников из Приложения 3 (уже сформированного автоматически)
        appendix_3 = Document.objects.filter(
            document_type=DocumentType.APPENDIX_3,
            organization=employer,
            year=year
        ).first()
        
        if not appendix_3:
            raise ValueError("Сначала нужно сформировать Приложение 3")
        
        employees_ids = [e['id'] for e in appendix_3.content.get('employees', [])]
        employees = Employee.objects.filter(id__in=employees_ids)
        
        # Распределяем по датам с учетом пропускной способности клиники и диапазона дат
        capacity = clinic.capacity_per_day or 50  # По умолчанию 50 человек в день
        plan_data = {}
        current_date = start_date.date()
        end_date_obj = end_date.date() if end_date else None
        
        employees_list = list(employees)
        employee_index = 0
        
        # Распределяем сотрудников по датам в указанном диапазоне
        while employee_index < len(employees_list):
            # Проверяем, не вышли ли за пределы диапазона
            if end_date_obj and current_date > end_date_obj:
                # Если вышли за пределы диапазона, распределяем оставшихся в последний день
                if employee_index < len(employees_list):
                    last_date = end_date_obj
                    if str(last_date) not in plan_data:
                        plan_data[str(last_date)] = []
                    # Добавляем всех оставшихся сотрудников в последний день
                    while employee_index < len(employees_list):
                        employee = employees_list[employee_index]
                        plan_data[str(last_date)].append({
                            'employee_id': employee.id,
                            'full_name': employee.full_name,
                            'position': employee.position.name if employee.position else 'Не указана',
                        })
                        employee_index += 1
                break
            
            # Инициализируем список сотрудников для текущего дня
            if str(current_date) not in plan_data:
                plan_data[str(current_date)] = []
            
            # Заполняем текущий день до capacity
            while (len(plan_data[str(current_date)]) < capacity and 
                   employee_index < len(employees_list)):
                employee = employees_list[employee_index]
                plan_data[str(current_date)].append({
                    'employee_id': employee.id,
                    'full_name': employee.full_name,
                    'position': employee.position.name if employee.position else 'Не указана',
                })
                employee_index += 1
            
            # Если день заполнен или все сотрудники распределены, переходим к следующему дню
            if len(plan_data[str(current_date)]) >= capacity:
                current_date += timedelta(days=1)
            elif employee_index >= len(employees_list):
                # Все сотрудники распределены, выходим из цикла
                break
        
        # Если не указан end_date и остались нераспределенные сотрудники, продолжаем
        if employee_index < len(employees_list) and not end_date_obj:
            while employee_index < len(employees_list):
                if str(current_date) not in plan_data:
                    plan_data[str(current_date)] = []
                
                while (len(plan_data[str(current_date)]) < capacity and 
                       employee_index < len(employees_list)):
                    employee = employees_list[employee_index]
                    plan_data[str(current_date)].append({
                        'employee_id': employee.id,
                        'full_name': employee.full_name,
                        'position': employee.position.name if employee.position else 'Не указана',
                    })
                    employee_index += 1
                
                if len(plan_data[str(current_date)]) >= capacity:
                    current_date += timedelta(days=1)
        
        # Удаляем пустые дни из плана
        plan_data = {date: employees for date, employees in plan_data.items() if employees}
        
        # Проверяем, существует ли уже календарный план на этот год для этого работодателя
        # Если существует - обновляем его, если нет - создаем новый
        calendar_plan, created = CalendarPlan.objects.get_or_create(
            employer=employer,
            year=year,
            defaults={
                'clinic': clinic,
                'plan_data': plan_data
            }
        )
        
        # Если план уже существовал, обновляем его данные
        if not created:
            calendar_plan.clinic = clinic
            calendar_plan.plan_data = plan_data
            calendar_plan.save()
        
        # Проверяем, существует ли уже документ для этого календарного плана
        if calendar_plan.document:
            # Обновляем существующий документ
            document = calendar_plan.document
            document.title = f"Календарный план проведения обязательных медицинских осмотров на {year} год"
            document.content = {
                'plan_data': plan_data,
                'clinic_name': clinic.name,
                'generated_at': timezone.now().isoformat(),
            }
            document.save()
        else:
            # Создаем новый документ календарного плана
            document = Document.objects.create(
                document_type=DocumentType.CALENDAR_PLAN,
                title=f"Календарный план проведения обязательных медицинских осмотров на {year} год",
                organization=employer,
                year=year,
                content={
                    'plan_data': plan_data,
                    'clinic_name': clinic.name,
                    'generated_at': timezone.now().isoformat(),
                }
            )
            calendar_plan.document = document
            calendar_plan.save()
        
        # Автоматически создаем осмотры из календарного плана
        DocumentService.create_examinations_from_calendar_plan(calendar_plan)
        
        return calendar_plan
    
    @staticmethod
    def create_examinations_from_calendar_plan(calendar_plan: CalendarPlan):
        """
        Автоматически создает осмотры из календарного плана и отправляет уведомления
        
        Args:
            calendar_plan: Календарный план
        """
        from apps.medical_examinations.services import ExaminationService
        from apps.authentication.services import GreenAPIService
        
        plan_data = calendar_plan.plan_data
        employer = calendar_plan.employer
        clinic = calendar_plan.clinic
        
        examinations_created = []
        
        for date_str, employees_list in plan_data.items():
            # Парсим дату
            from datetime import datetime as dt
            scheduled_date = dt.strptime(date_str, '%Y-%m-%d').date()
            # Устанавливаем время на 9:00
            scheduled_datetime = timezone.make_aware(
                dt.combine(scheduled_date, dt.min.time().replace(hour=9))
            )
            
            for emp_data in employees_list:
                try:
                    employee = Employee.objects.get(id=emp_data['employee_id'])
                    
                    # Создаем осмотр
                    examination = ExaminationService.create_examination(
                        employee=employee,
                        examination_type='periodic',
                        clinic=clinic,
                        scheduled_date=scheduled_datetime,
                        employer=employer
                    )
                    examinations_created.append(examination)
                    
                    # Отправляем уведомление сотруднику с QR-кодом
                    if employee.user.phone_number:
                        message = (
                            f"Вам назначен обязательный медицинский осмотр.\n"
                            f"📅 Дата: {scheduled_date.strftime('%d.%m.%Y')}\n"
                            f"🏥 Клиника: {clinic.name}\n"
                            f"📍 Адрес: {clinic.address or 'Уточните в клинике'}\n"
                            f"🔐 Ваш QR-код для доступа:\n{examination.qr_code}\n\n"
                            f"Приходите в клинику и покажите QR-код регистратору."
                        )
                        try:
                            GreenAPIService.send_whatsapp_message(
                                employee.user.phone_number,
                                message
                            )
                        except Exception as e:
                            # Логируем ошибку, но не прерываем процесс
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Ошибка отправки уведомления: {e}")
                
                except Employee.DoesNotExist:
                    continue
        
        return examinations_created
    
    @staticmethod
    def generate_final_act(
        employer: Organization,
        clinic: Organization,
        year: int
    ) -> Document:
        """
        Генерация Заключительного акта по результатам осмотров
        
        Согласно Пункту 20.5 Приказа 131 (трехсторонний)
        """
        # Получаем все завершенные осмотры за год
        examinations = MedicalExamination.objects.filter(
            employer=employer,
            clinic=clinic,
            status='completed',
            completed_date__year=year
        )
        
        # Статистика
        total_examined = examinations.count()
        fit_count = examinations.filter(result=ExaminationResult.FIT).count()
        unfit_count = examinations.filter(result=ExaminationResult.UNFIT).count()
        limited_count = examinations.filter(result=ExaminationResult.LIMITED).count()
        
        # Лица с профзаболеваниями
        professional_diseases = []
        # Лица для перевода
        transfer_needed = []
        
        for exam in examinations:
            if exam.result == ExaminationResult.UNFIT:
                professional_diseases.append({
                    'employee_id': exam.employee.id,
                    'full_name': exam.employee.full_name,
                    'position': exam.employee.position.name,
                })
            
            if exam.result == ExaminationResult.LIMITED:
                transfer_needed.append({
                    'employee_id': exam.employee.id,
                    'full_name': exam.employee.full_name,
                    'position': exam.employee.position.name,
                    'recommendations': exam.doctor_examinations.first().recommendations if exam.doctor_examinations.exists() else '',
                })
        
        # Создаем документ
        document = Document.objects.create(
            document_type=DocumentType.FINAL_ACT,
            title=f"Заключительный акт по результатам периодических медицинских осмотров {year} года",
            organization=employer,
            year=year,
            status='pending_signature',
            content={
                'employer_name': employer.name,
                'clinic_name': clinic.name,
                'year': year,
                'statistics': {
                    'total_examined': total_examined,
                    'fit': fit_count,
                    'unfit': unfit_count,
                    'limited': limited_count,
                },
                'professional_diseases': professional_diseases,
                'transfer_needed': transfer_needed,
                'generated_at': timezone.now().isoformat(),
            }
        )
        
        return document
    
    @staticmethod
    def request_signature(document: Document, signer_role: str) -> DocumentSignature:
        """
        Запросить подпись документа через OTP
        
        Args:
            document: Документ
            signer_role: Роль подписанта (clinic/employer/ses)
            
        Returns:
            DocumentSignature объект
        """
        # Определяем подписанта по роли
        if signer_role == 'clinic':
            signer = document.organization.owner  # Владелец клиники
        elif signer_role == 'employer':
            signer = document.organization.owner  # Владелец работодателя
        else:
            raise ValueError(f"Неизвестная роль: {signer_role}")
        
        # Создаем или получаем подпись
        signature, created = DocumentSignature.objects.get_or_create(
            document=document,
            role=signer_role,
            defaults={'signer': signer}
        )
        
        # Генерируем и отправляем OTP
        otp_code = OTPService.generate_code()
        signature.otp_code = otp_code
        signature.otp_sent_at = timezone.now()
        signature.save()
        
        # Отправляем OTP на WhatsApp
        from apps.authentication.services import GreenAPIService
        message = f"Код для подписания документа '{document.title}': {otp_code}\nКод действителен 5 минут."
        GreenAPIService.send_whatsapp_message(signer.phone_number, message)
        
        return signature
    
    @staticmethod
    def verify_and_sign(
        document: Document,
        signer_role: str,
        otp_code: str,
        ip_address: str = '',
        user_agent: str = ''
    ) -> DocumentSignature:
        """
        Проверить OTP и подписать документ
        
        Args:
            document: Документ
            signer_role: Роль подписанта
            otp_code: OTP код
            ip_address: IP адрес
            user_agent: User Agent
            
        Returns:
            DocumentSignature объект
        """
        signature = DocumentSignature.objects.get(
            document=document,
            role=signer_role
        )
        
        # Проверяем OTP
        if signature.otp_code != otp_code:
            raise ValueError("Неверный OTP код")
        
        if signature.otp_sent_at:
            from datetime import timedelta
            if timezone.now() - signature.otp_sent_at > timedelta(minutes=5):
                raise ValueError("OTP код истек")
        
        # Подписываем
        signature.otp_verified = True
        signature.signed_at = timezone.now()
        signature.ip_address = ip_address
        signature.user_agent = user_agent
        signature.save()
        
        # Проверяем, все ли подписи собраны
        total_signatures = DocumentSignature.objects.filter(document=document).count()
        verified_signatures = DocumentSignature.objects.filter(
            document=document,
            otp_verified=True
        ).count()
        
        if verified_signatures == total_signatures:
            document.status = 'signed'
            document.save()
        
        return signature
    
    @staticmethod
    def generate_medical_certificate(examination: MedicalExamination) -> Document:
        """
        Генерация справки 075/у после завершения осмотра
        
        Args:
            examination: Завершенный осмотр
            
        Returns:
            Document объект (справка 075/у)
        """
        # Собираем данные для справки
        doctor_examinations = examination.doctor_examinations.all()
        findings_summary = []
        
        for doc_exam in doctor_examinations:
            findings_summary.append({
                'doctor': doc_exam.doctor.user.phone_number,
                'specialization': doc_exam.doctor.specialization or 'Врач',
                'harmful_factor': doc_exam.harmful_factor.name,
                'result': doc_exam.get_result_display(),
                'findings': doc_exam.findings,
            })
        
        # Получаем профпатолога из маршрута
        profpathologist = None
        if examination.route:
            profpathologist_obj = examination.route.doctors_required.filter(role='profpathologist').first()
            if profpathologist_obj:
                profpathologist = {'phone': profpathologist_obj.user.phone_number}
        
        # Формируем справку
        certificate = Document.objects.create(
            document_type=DocumentType.MEDICAL_CERTIFICATE,
            title=f"Справка 075/у - {examination.employee.full_name}",
            organization=examination.employer or examination.employee.employer,
            year=examination.completed_date.year if examination.completed_date else timezone.now().year,
            examination=examination,
            status='signed',  # Справка сразу считается подписанной профпатологом
            content={
                'employee': {
                    'full_name': examination.employee.full_name,
                    'iin': examination.employee.iin,
                    'position': examination.employee.position.name if examination.employee.position else '',
                    'department': examination.employee.department,
                },
                'employer': {
                    'name': (examination.employer or examination.employee.employer).name,
                },
                'clinic': {
                    'name': examination.clinic.name,
                    'address': examination.clinic.address,
                },
                'examination_date': examination.completed_date.isoformat() if examination.completed_date else timezone.now().isoformat(),
                'result': examination.result,
                'result_display': examination.get_result_display(),
                'doctor_examinations': findings_summary,
                'profpathologist': profpathologist or {},
                'generated_at': timezone.now().isoformat(),
            }
        )
        
        return certificate

