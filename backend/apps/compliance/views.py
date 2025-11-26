"""
Compliance views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import HarmfulFactor, Profession, MedicalContraindication
from .serializers import (
    HarmfulFactorSerializer,
    ProfessionSerializer,
    MedicalContraindicationSerializer
)
from .services import ComplianceService


class HarmfulFactorViewSet(viewsets.ModelViewSet):
    """ViewSet для вредных факторов"""
    queryset = HarmfulFactor.objects.filter(is_active=True)
    serializer_class = HarmfulFactorSerializer
    permission_classes = [IsAuthenticated]


class ProfessionViewSet(viewsets.ModelViewSet):
    """ViewSet для профессий"""
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def auto_map_factors(self, request):
        """Авто-маппинг факторов по названию профессии"""
        profession_name = request.data.get('profession_name', '')
        
        if not profession_name:
            return Response(
                {'error': 'Укажите название профессии'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        factors = ComplianceService.auto_map_factors(profession_name)
        serializer = HarmfulFactorSerializer(factors, many=True)
        
        return Response({
            'profession_name': profession_name,
            'factors': serializer.data,
            'found': len(factors) > 0
        })


class MedicalContraindicationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для противопоказаний (только чтение)"""
    queryset = MedicalContraindication.objects.all()
    serializer_class = MedicalContraindicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        harmful_factor_id = self.request.query_params.get('harmful_factor_id')
        if harmful_factor_id:
            return self.queryset.filter(harmful_factor_id=harmful_factor_id)
        return self.queryset

