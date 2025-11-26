"""
Compliance serializers
"""
from rest_framework import serializers
from .models import HarmfulFactor, Profession, MedicalContraindication


class HarmfulFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarmfulFactor
        fields = [
            'id', 'code', 'name', 'description', 'periodicity_months',
            'required_doctors', 'required_tests', 'is_active'
        ]


class ProfessionSerializer(serializers.ModelSerializer):
    harmful_factors = HarmfulFactorSerializer(many=True, read_only=True)
    harmful_factor_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=HarmfulFactor.objects.all(),
        write_only=True,
        source='harmful_factors'
    )
    
    class Meta:
        model = Profession
        fields = [
            'id', 'name', 'harmful_factors', 'harmful_factor_ids',
            'is_decreted', 'keywords'
        ]


class MedicalContraindicationSerializer(serializers.ModelSerializer):
    harmful_factor_name = serializers.CharField(source='harmful_factor.name', read_only=True)
    
    class Meta:
        model = MedicalContraindication
        fields = [
            'id', 'harmful_factor', 'harmful_factor_name', 'condition',
            'icd_code', 'severity'
        ]

