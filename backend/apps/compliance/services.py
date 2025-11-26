"""
Compliance services - Бизнес-логика Приказа 131
"""
from typing import List, Optional
from .models import Profession, HarmfulFactor


class ComplianceService:
    """Сервис для работы с Compliance данными"""
    
    @staticmethod
    def auto_map_factors(profession_name: str) -> List[HarmfulFactor]:
        """
        Автоматический подбор вредных факторов по названию профессии
        
        Args:
            profession_name: Название профессии/должности
            
        Returns:
            Список вредных факторов
        """
        profession_name_lower = profession_name.lower()
        
        # Ищем профессию по точному совпадению
        try:
            profession = Profession.objects.get(name__iexact=profession_name)
            return list(profession.harmful_factors.filter(is_active=True))
        except Profession.DoesNotExist:
            pass
        
        # Ищем по ключевым словам
        professions = Profession.objects.filter(
            keywords__icontains=profession_name_lower
        )
        
        if professions.exists():
            # Берем первую найденную профессию
            profession = professions.first()
            return list(profession.harmful_factors.filter(is_active=True))
        
        # Поиск по частичному совпадению названия
        professions = Profession.objects.filter(
            name__icontains=profession_name_lower
        )
        
        if professions.exists():
            profession = professions.first()
            return list(profession.harmful_factors.filter(is_active=True))
        
        # Если ничего не найдено, возвращаем пустой список
        return []
    
    @staticmethod
    def get_required_doctors_for_factors(factors: List[HarmfulFactor]) -> List[str]:
        """
        Получить список требуемых врачей для данных факторов
        
        Args:
            factors: Список вредных факторов
            
        Returns:
            Список специализаций врачей
        """
        required_doctors = set()
        
        for factor in factors:
            if factor.required_doctors:
                required_doctors.update(factor.required_doctors)
        
        return list(required_doctors)
    
    @staticmethod
    def get_required_tests_for_factors(factors: List[HarmfulFactor]) -> List[str]:
        """
        Получить список требуемых анализов для данных факторов
        
        Args:
            factors: Список вредных факторов
            
        Returns:
            Список анализов
        """
        required_tests = set()
        
        for factor in factors:
            if factor.required_tests:
                required_tests.update(factor.required_tests)
        
        return list(required_tests)
    
    @staticmethod
    def check_contraindications(
        harmful_factor: HarmfulFactor,
        findings: str,
        icd_codes: Optional[List[str]] = None
    ) -> List[dict]:
        """
        Проверка противопоказаний по результатам осмотра
        
        Args:
            harmful_factor: Вредный фактор
            findings: Заключение врача
            icd_codes: Список кодов МКБ-10 (опционально)
            
        Returns:
            Список найденных противопоказаний
        """
        contraindications = []
        
        # Получаем все противопоказания для этого фактора
        all_contraindications = harmful_factor.contraindications.all()
        
        findings_lower = findings.lower()
        
        for contraindication in all_contraindications:
            condition_lower = contraindication.condition.lower()
            
            # Проверяем по тексту заключения
            if condition_lower in findings_lower or findings_lower in condition_lower:
                contraindications.append({
                    'id': contraindication.id,
                    'condition': contraindication.condition,
                    'icd_code': contraindication.icd_code,
                    'severity': contraindication.severity,
                })
            
            # Проверяем по коду МКБ-10
            if icd_codes and contraindication.icd_code:
                if contraindication.icd_code in icd_codes:
                    contraindications.append({
                        'id': contraindication.id,
                        'condition': contraindication.condition,
                        'icd_code': contraindication.icd_code,
                        'severity': contraindication.severity,
                    })
        
        return contraindications

