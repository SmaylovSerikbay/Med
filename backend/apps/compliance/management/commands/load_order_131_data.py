"""
Команда для загрузки базовых данных Приказа 131
"""
from django.core.management.base import BaseCommand
from apps.compliance.models import HarmfulFactor, Profession, MedicalContraindication


class Command(BaseCommand):
    help = 'Загружает базовые данные из Приказа 131 (вредные факторы, профессии)'

    def handle(self, *args, **options):
        # Базовые вредные факторы (примеры из Приказа 131)
        factors_data = [
            {
                'code': '1.1.1',
                'name': 'Промышленная пыль',
                'periodicity_months': 12,
                'required_doctors': ['терапевт', 'оториноларинголог', 'пульмонолог'],
                'required_tests': ['рентген легких', 'спирография'],
            },
            {
                'code': '1.2.1',
                'name': 'Шум',
                'periodicity_months': 12,
                'required_doctors': ['оториноларинголог', 'невролог'],
                'required_tests': ['аудиометрия'],
            },
            {
                'code': '1.3.1',
                'name': 'Ультрафиолетовое излучение',
                'periodicity_months': 12,
                'required_doctors': ['офтальмолог', 'дерматолог'],
                'required_tests': ['осмотр глазного дна'],
            },
            {
                'code': '2.1.1',
                'name': 'Сварочные аэрозоли',
                'periodicity_months': 12,
                'required_doctors': ['терапевт', 'оториноларинголог', 'пульмонолог'],
                'required_tests': ['рентген легких', 'спирография', 'общий анализ крови'],
            },
            {
                'code': '3.1.1',
                'name': 'Работа на высоте',
                'periodicity_months': 12,
                'required_doctors': ['терапевт', 'офтальмолог', 'невролог'],
                'required_tests': ['ЭКГ', 'вестибулометрия'],
            },
        ]

        for factor_data in factors_data:
            factor, created = HarmfulFactor.objects.get_or_create(
                code=factor_data['code'],
                defaults={
                    'name': factor_data['name'],
                    'periodicity_months': factor_data['periodicity_months'],
                    'required_doctors': factor_data['required_doctors'],
                    'required_tests': factor_data['required_tests'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан фактор: {factor.code} - {factor.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Фактор уже существует: {factor.code}'))

        # Базовые профессии с авто-маппингом
        professions_data = [
            {
                'name': 'Электросварщик',
                'keywords': ['сварщик', 'сварка', 'электросварщик'],
                'factor_codes': ['2.1.1', '1.3.1', '1.2.1'],
            },
            {
                'name': 'Шахтер',
                'keywords': ['шахтер', 'шахта', 'горнорабочий'],
                'factor_codes': ['1.1.1', '1.2.1'],
            },
            {
                'name': 'Крановщик',
                'keywords': ['крановщик', 'кран', 'машинист крана'],
                'factor_codes': ['3.1.1', '1.2.1'],
            },
            {
                'name': 'Повар',
                'keywords': ['повар', 'кухня', 'общепит'],
                'factor_codes': [],
                'is_decreted': True,
            },
            {
                'name': 'Учитель',
                'keywords': ['учитель', 'педагог', 'преподаватель'],
                'factor_codes': [],
                'is_decreted': True,
            },
        ]

        for prof_data in professions_data:
            profession, created = Profession.objects.get_or_create(
                name=prof_data['name'],
                defaults={
                    'keywords': prof_data['keywords'],
                    'is_decreted': prof_data.get('is_decreted', False),
                }
            )
            
            # Привязываем факторы
            if prof_data['factor_codes']:
                factors = HarmfulFactor.objects.filter(code__in=prof_data['factor_codes'])
                profession.harmful_factors.set(factors)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана профессия: {profession.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Профессия уже существует: {profession.name}'))

        # Базовые противопоказания
        contraindications_data = [
            {
                'factor_code': '1.1.1',
                'condition': 'Хронические заболевания легких с дыхательной недостаточностью',
                'icd_code': 'J44',
                'severity': 'critical',
            },
            {
                'factor_code': '1.2.1',
                'condition': 'Стойкое снижение слуха',
                'icd_code': 'H90',
                'severity': 'critical',
            },
            {
                'factor_code': '3.1.1',
                'condition': 'Острота зрения ниже 0.8',
                'icd_code': 'H52',
                'severity': 'critical',
            },
            {
                'factor_code': '3.1.1',
                'condition': 'Эпилепсия',
                'icd_code': 'G40',
                'severity': 'critical',
            },
        ]

        for contra_data in contraindications_data:
            try:
                factor = HarmfulFactor.objects.get(code=contra_data['factor_code'])
                contraindication, created = MedicalContraindication.objects.get_or_create(
                    harmful_factor=factor,
                    condition=contra_data['condition'],
                    defaults={
                        'icd_code': contra_data['icd_code'],
                        'severity': contra_data['severity'],
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Создано противопоказание: {contraindication.condition}')
                    )
            except HarmfulFactor.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Фактор не найден: {contra_data["factor_code"]}')
                )

        self.stdout.write(self.style.SUCCESS('\nДанные Приказа 131 успешно загружены!'))

