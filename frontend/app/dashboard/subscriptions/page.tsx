'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { subscriptionsAPI, organizationsAPI } from '@/lib/api'
import { CreditCard, CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react'

export default function SubscriptionsPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const { profile } = useUserStore()
  const [plans, setPlans] = useState<any[]>([])
  const [subscriptions, setSubscriptions] = useState<any[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedOrg, setSelectedOrg] = useState<number | null>(null)
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    loadData()
  }, [isAuthenticated, router])

  const loadData = async () => {
    try {
      const [plansRes, subsRes, orgsRes] = await Promise.all([
        subscriptionsAPI.getPlans(),
        subscriptionsAPI.getCurrent(),
        organizationsAPI.list(),
      ])
      setPlans(plansRes.data.results || plansRes.data)
      const subs = subsRes.data.results || subsRes.data
      const orgs = orgsRes.data.results || orgsRes.data
      
      // Создаем подписки для организаций где их нет (со статусом 'none')
      const orgsWithSubs = new Set(subs.map((s: any) => s.organization))
      const orgsWithoutSubs = orgs.filter((org: any) => !orgsWithSubs.has(org.id))
      
      // Добавляем виртуальные подписки со статусом 'none' для организаций без подписки
      const allSubs = [
        ...subs,
        ...orgsWithoutSubs.map((org: any) => ({
          id: null,
          organization: org.id,
          organization_name: org.name,
          organization_type: org.org_type,
          plan: null,
          plan_name: null,
          status: 'none',
          is_active: false,
        }))
      ]
      
      setSubscriptions(allSubs)
      setOrganizations(orgs)
      
      // Автоматически выбираем первую организацию без активной подписки
      const orgsWithoutActiveSub = orgs.filter((org: any) => {
        const sub = allSubs.find((s: any) => s.organization === org.id)
        return !sub || !sub.is_active
      })
      if (orgsWithoutActiveSub.length > 0 && !selectedOrg) {
        setSelectedOrg(orgsWithoutActiveSub[0].id)
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRequestSubscription = async () => {
    if (!selectedOrg || !selectedPlan) {
      alert('Выберите организацию и план подписки')
      return
    }

    try {
      const response = await subscriptionsAPI.requestSubscription(selectedOrg, selectedPlan)
      alert('Подписка запрошена! Ожидайте одобрения администратора.')
      await loadData()
      
      // Перезагружаем профиль чтобы обновилась информация
      const { loadProfile } = useUserStore.getState()
      await loadProfile()
    } catch (error: any) {
      const errorMsg = error.response?.data?.error || error.response?.data?.message || 'Ошибка запроса подписки'
      alert(errorMsg)
      console.error('Ошибка запроса подписки:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />
      case 'expired':
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'expired':
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (!isAuthenticated) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Подписки</h1>
          <p className="text-gray-600 mt-2">Управление подписками ваших организаций</p>
        </div>

        {/* Запрос новой подписки */}
        <Card className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Запросить подписку</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Организация *
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={selectedOrg || ''}
                onChange={(e) => setSelectedOrg(parseInt(e.target.value))}
              >
                <option value="">Выберите организацию</option>
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>{org.name} ({org.org_type === 'clinic' ? 'Клиника' : 'Работодатель'})</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                План подписки *
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={selectedPlan || ''}
                onChange={(e) => setSelectedPlan(parseInt(e.target.value))}
              >
                <option value="">Выберите план</option>
                {plans.map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name} - {plan.price_monthly} ₸/мес
                    {plan.max_employees && ` (до ${plan.max_employees} сотрудников)`}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <Button
            onClick={handleRequestSubscription}
            disabled={!selectedOrg || !selectedPlan}
          >
            <CreditCard className="w-4 h-4 mr-2" />
            Запросить подписку
          </Button>
        </Card>

        {/* Текущие подписки */}
        {loading ? (
          <div className="text-center py-12">Загрузка...</div>
        ) : subscriptions.length === 0 ? (
          <Card className="text-center py-12">
            <CreditCard className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Нет организаций</p>
            <p className="text-sm text-gray-500 mt-2">
              Создайте организацию чтобы запросить подписку
            </p>
          </Card>
        ) : (
          <div className="space-y-4">
            {subscriptions.map((sub, index) => (
              <Card key={sub.id || `org-${sub.organization}-${index}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(sub.status)}
                      <h3 className="text-lg font-semibold">{sub.organization_name}</h3>
                      <span className={`px-2 py-1 text-xs rounded ${getStatusColor(sub.status)}`}>
                        {sub.status === 'active' ? 'Активна' :
                         sub.status === 'pending' ? 'Ожидает одобрения' :
                         sub.status === 'expired' ? 'Истекла' :
                         sub.status === 'cancelled' ? 'Отменена' :
                         sub.status === 'none' ? 'Нет подписки' :
                         'Нет подписки'}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      {sub.status !== 'none' && (
                        <>
                          <div>
                            <span className="font-medium">План:</span> {sub.plan_name}
                          </div>
                          {sub.started_at && (
                            <div>
                              <span className="font-medium">Начало:</span>{' '}
                              {new Date(sub.started_at).toLocaleDateString('ru-RU')}
                            </div>
                          )}
                          {sub.expires_at && (
                            <div>
                              <span className="font-medium">Истекает:</span>{' '}
                              {new Date(sub.expires_at).toLocaleDateString('ru-RU')}
                            </div>
                          )}
                          {sub.approved_by_phone && (
                            <div>
                              <span className="font-medium">Одобрено:</span>{' '}
                              {sub.approved_by_phone}
                            </div>
                          )}
                        </>
                      )}
                      {sub.status === 'none' && (
                        <div className="col-span-4">
                          <p className="text-gray-500 italic">
                            Подписка не запрошена. Выберите план и запросите подписку выше.
                          </p>
                        </div>
                      )}
                    </div>
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

