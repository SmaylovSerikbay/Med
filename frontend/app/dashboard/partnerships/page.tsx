'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { partnershipsAPI, organizationsAPI } from '@/lib/api'
import { Building2, Stethoscope, CheckCircle, XCircle, Clock, ArrowRight } from 'lucide-react'
import { Loading } from '@/components/ui/Loading'

export default function PartnershipsPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const { profile } = useUserStore()
  const [partnerships, setPartnerships] = useState<any[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])
  const [availableClinics, setAvailableClinics] = useState<any[]>([])
  const [loadingClinics, setLoadingClinics] = useState(false)
  const [loading, setLoading] = useState(true)
  const [showRequestForm, setShowRequestForm] = useState(false)
  const [requestData, setRequestData] = useState({
    clinic_id: '',
    employer_id: '',
    default_price: 5000,
  })

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    loadData()
  }, [isAuthenticated, router])

  const loadData = async () => {
    try {
      const [partnershipsRes, orgsRes] = await Promise.all([
        partnershipsAPI.list(),
        organizationsAPI.list(),
      ])
      setPartnerships(partnershipsRes.data.results || partnershipsRes.data)
      const orgs = orgsRes.data.results || orgsRes.data
      setOrganizations(orgs)
      
      // Сохраняем клиники отдельно для использования в fallback
      const clinics = orgs.filter((o: any) => o.org_type === 'clinic')
      console.log('Загружены организации:', orgs.length, 'из них клиник:', clinics.length)
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadAvailableClinics = async (employerId: number) => {
    if (!employerId) {
      setAvailableClinics([])
      return
    }
    
    setLoadingClinics(true)
    try {
      console.log('Загружаем доступные клиники для работодателя:', employerId)
      
      // Сначала пробуем получить все клиники через getAllClinics (более надежный способ)
      try {
        console.log('Загружаем все клиники через organizationsAPI.getAllClinics()')
        const allClinicsRes = await organizationsAPI.getAllClinics()
        const allClinics = allClinicsRes.data || []
        console.log('Все клиники из getAllClinics:', allClinics.length, allClinics)
        
        if (allClinics.length > 0) {
          // Фильтруем клиники, с которыми уже есть партнерства
          const existingPartnershipClinicIds = partnerships
            .filter((p: any) => 
              p.employer === parseInt(String(employerId)) && 
              (p.status === 'active' || p.status === 'pending')
            )
            .map((p: any) => p.clinic)
          
          const available = allClinics.filter((c: any) => !existingPartnershipClinicIds.includes(c.id))
          console.log('Доступные клиники после фильтрации:', available.length, available)
          setAvailableClinics(available)
          return
        }
      } catch (getAllClinicsError: any) {
        console.warn('Ошибка загрузки всех клиник через getAllClinics:', getAllClinicsError)
      }
      
      // Fallback: пробуем availableClinics API
      try {
        const response = await partnershipsAPI.availableClinics(employerId)
        console.log('Ответ API availableClinics:', response)
        const clinics = response.data || []
        console.log('Загружены клиники из availableClinics:', clinics.length, clinics)
        setAvailableClinics(clinics)
      } catch (availableClinicsError: any) {
        console.warn('Ошибка загрузки через availableClinics:', availableClinicsError)
        
        // Последний fallback: используем организации из кэша
        const allClinics = organizations.filter((o: any) => o.org_type === 'clinic')
        console.log('Используем клиники из кэша organizations:', allClinics.length, allClinics)
        
        if (allClinics.length > 0) {
          // Фильтруем существующие партнерства
          const existingPartnershipClinicIds = partnerships
            .filter((p: any) => 
              p.employer === parseInt(String(employerId)) && 
              (p.status === 'active' || p.status === 'pending')
            )
            .map((p: any) => p.clinic)
          
          const available = allClinics.filter((c: any) => !existingPartnershipClinicIds.includes(c.id))
          setAvailableClinics(available)
        } else {
          setAvailableClinics([])
        }
      }
    } catch (error: any) {
      console.error('Критическая ошибка загрузки клиник:', error)
      setAvailableClinics([])
    } finally {
      setLoadingClinics(false)
    }
  }

  const handleRequestPartnership = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await partnershipsAPI.requestPartnership(
        parseInt(requestData.employer_id),
        parseInt(requestData.clinic_id),
        requestData.default_price
      )
      setShowRequestForm(false)
      setRequestData({ clinic_id: '', employer_id: '', default_price: 5000 })
      loadData()
      alert('Запрос на партнерство отправлен!')
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка запроса партнерства')
    }
  }

  const handleConfirm = async (partnershipId: number) => {
    const defaultPrice = prompt('Введите цену (тенге):', '5000')
    if (!defaultPrice) return
    
    try {
      await partnershipsAPI.confirm(partnershipId, {}, parseFloat(defaultPrice))
      loadData()
      alert('Партнерство подтверждено!')
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка подтверждения')
    }
  }

  const handleReject = async (partnershipId: number) => {
    if (!confirm('Отклонить запрос на партнерство?')) return
    
    try {
      await partnershipsAPI.reject(partnershipId)
      loadData()
      alert('Запрос отклонен')
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка отклонения')
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Активно</span>
      case 'pending':
        return <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">Ожидает</span>
      case 'rejected':
        return <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">Отклонено</span>
      default:
        return <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">{status}</span>
    }
  }

  const userOrganizations = profile?.organizations || []
  const userClinics = userOrganizations.filter((o: any) => o.type === 'clinic')
  const userEmployers = userOrganizations.filter((o: any) => o.type === 'employer')
  const isClinicOwner = profile?.roles?.includes('clinic_owner')
  const isEmployerOwner = userEmployers.length > 0

  if (!isAuthenticated || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Партнерства</h1>
            <p className="text-gray-600 mt-2">Управление партнерствами между клиниками и работодателями</p>
          </div>
          {isEmployerOwner && (
            <Button onClick={() => setShowRequestForm(true)}>
              Запросить партнерство
            </Button>
          )}
        </div>

        {showRequestForm && isEmployerOwner && (
          <Card className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Запросить партнерство</h2>
            <form onSubmit={handleRequestPartnership} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Работодатель
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    value={requestData.employer_id}
                    onChange={(e) => {
                      const employerId = e.target.value
                      setRequestData({ ...requestData, employer_id: employerId, clinic_id: '' })
                      if (employerId) {
                        loadAvailableClinics(parseInt(employerId))
                      } else {
                        setAvailableClinics([])
                      }
                    }}
                    required
                  >
                    <option value="">Выберите работодателя</option>
                    {userEmployers.map((org: any) => (
                      <option key={org.id} value={org.id}>{org.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Клиника
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    value={requestData.clinic_id}
                    onChange={(e) => setRequestData({ ...requestData, clinic_id: e.target.value })}
                    required
                    disabled={!requestData.employer_id || loadingClinics}
                  >
                    <option value="">
                      {loadingClinics 
                        ? 'Загрузка клиник...' 
                        : !requestData.employer_id 
                        ? 'Сначала выберите работодателя'
                        : 'Выберите клинику'}
                    </option>
                    {availableClinics.map((clinic: any) => (
                      <option key={clinic.id} value={clinic.id}>{clinic.name}</option>
                    ))}
                  </select>
                  {!loadingClinics && requestData.employer_id && availableClinics.length === 0 && (
                    <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-sm text-yellow-800 font-medium mb-1">
                        Нет доступных клиник для запроса партнерства
                      </p>
                      <p className="text-xs text-yellow-700">
                        Это может означать, что:
                        <br />• Все клиники уже имеют партнерство с выбранным работодателем
                        <br />• В системе еще нет зарегистрированных клиник
                        <br />• Проверьте консоль браузера (F12) для деталей
                      </p>
                    </div>
                  )}
                </div>
                <Input
                  label="Предлагаемая цена (тенге)"
                  type="number"
                  value={requestData.default_price}
                  onChange={(e) => setRequestData({ ...requestData, default_price: parseFloat(e.target.value) })}
                  required
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit">Отправить запрос</Button>
                <Button type="button" variant="outline" onClick={() => setShowRequestForm(false)}>
                  Отмена
                </Button>
              </div>
            </form>
          </Card>
        )}

        {loading ? (
          <div className="text-center py-12">
            <Loading />
          </div>
        ) : partnerships.length === 0 ? (
          <Card className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Нет партнерств</p>
          </Card>
        ) : (
          <div className="space-y-4">
            {partnerships.map((partnership: any) => (
              <Card key={partnership.id}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Stethoscope className="w-6 h-6 text-emerald-600" />
                      <h3 className="text-lg font-semibold">{partnership.clinic_name}</h3>
                      <span className="text-gray-400">↔</span>
                      <Building2 className="w-6 h-6 text-blue-600" />
                      <h3 className="text-lg font-semibold">{partnership.employer_name}</h3>
                      {getStatusBadge(partnership.status)}
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mt-4">
                      <div>
                        <span className="font-medium text-gray-900">Цена:</span> {partnership.default_price} ₸
                      </div>
                      <div>
                        <span className="font-medium text-gray-900">Запрошено:</span>{' '}
                        {new Date(partnership.requested_at).toLocaleDateString('ru-RU')}
                      </div>
                      {partnership.confirmed_at && (
                        <div>
                          <span className="font-medium text-gray-900">Подтверждено:</span>{' '}
                          {new Date(partnership.confirmed_at).toLocaleDateString('ru-RU')}
                        </div>
                      )}
                      {partnership.expires_at && (
                        <div>
                          <span className="font-medium text-gray-900">Действует до:</span>{' '}
                          {new Date(partnership.expires_at).toLocaleDateString('ru-RU')}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    {partnership.status === 'pending' && isClinicOwner && partnership.clinic === userClinics[0]?.id && (
                      <>
                        <Button size="sm" onClick={() => handleConfirm(partnership.id)}>
                          Подтвердить
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleReject(partnership.id)}>
                          Отклонить
                        </Button>
                      </>
                    )}
                    {partnership.status === 'active' && (
                      <span className="text-green-600 font-medium">✓ Активно</span>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

