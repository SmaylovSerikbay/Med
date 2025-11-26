'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { calendarPlansAPI } from '@/lib/api'
import { Calendar, Eye, FileText, Building2, Stethoscope } from 'lucide-react'

export default function CalendarPlansPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const [plans, setPlans] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    
    loadPlans()
  }, [isAuthenticated, router])

  const loadPlans = async () => {
    try {
      const response = await calendarPlansAPI.list()
      setPlans(response.data.results || response.data || [])
    } catch (error: any) {
      console.error('Ошибка загрузки планов:', error)
      if (error.response?.status === 403) {
        // Работодатель не имеет доступа или еще нет планов
        setPlans([])
      }
    } finally {
      setLoading(false)
    }
  }

  const { profile } = useUserStore()

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    } catch {
      return dateStr
    }
  }

  const getPlanStats = (plan: any) => {
    const planData = plan.plan_data || {}
    const dates = Object.keys(planData)
    const totalEmployees = dates.reduce((sum, date) => {
      return sum + (planData[date]?.length || 0)
    }, 0)
    
    return {
      totalDates: dates.length,
      totalEmployees,
      startDate: dates.length > 0 ? dates[0] : null,
      endDate: dates.length > 0 ? dates[dates.length - 1] : null,
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка календарных планов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Calendar className="w-8 h-8" />
              Календарные планы осмотров
            </h1>
            <p className="text-gray-600 mt-2">
              Просмотр календарных планов проведения медицинских осмотров, созданных партнерскими клиниками
            </p>
          </div>
          {/* Работодатель может только просматривать планы, созданные клиникой */}
        </div>

        {plans.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Нет календарных планов
              </h3>
              <p className="text-gray-600 mb-6">
                Календарные планы создаются клиникой после формирования Приложения 3.
                <br />
                Обратитесь к партнерской клинике для создания плана.
              </p>
            </div>
          </Card>
        ) : (
          <div className="grid gap-6">
            {plans.map((plan) => {
              const stats = getPlanStats(plan)
              
              return (
                <Card key={plan.id} className="hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-primary-100 rounded-lg">
                          <Calendar className="w-6 h-6 text-primary-600" />
                        </div>
                        <div>
                          <h3 className="text-xl font-semibold text-gray-900">
                            Календарный план на {plan.year} год
                          </h3>
                          <p className="text-sm text-gray-500 mt-1">
                            Создан {formatDate(plan.created_at)}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div className="flex items-start gap-2">
                          <Building2 className="w-5 h-5 text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-500">Работодатель</p>
                            <p className="font-medium text-gray-900">{plan.employer_name}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-2">
                          <Stethoscope className="w-5 h-5 text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-500">Клиника</p>
                            <p className="font-medium text-gray-900">{plan.clinic_name}</p>
                          </div>
                        </div>

                        <div className="flex items-start gap-2">
                          <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-500">Период</p>
                            {stats.startDate && stats.endDate ? (
                              <p className="font-medium text-gray-900">
                                {formatDate(stats.startDate)} - {formatDate(stats.endDate)}
                              </p>
                            ) : (
                              <p className="font-medium text-gray-900">Не указан</p>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-6 text-sm">
                        <div>
                          <span className="text-gray-500">Всего дней: </span>
                          <span className="font-semibold text-gray-900">{stats.totalDates}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Всего сотрудников: </span>
                          <span className="font-semibold text-gray-900">{stats.totalEmployees}</span>
                        </div>
                        {stats.totalDates > 0 && (
                          <div>
                            <span className="text-gray-500">Среднее в день: </span>
                            <span className="font-semibold text-gray-900">
                              {Math.ceil(stats.totalEmployees / stats.totalDates)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="ml-4">
                      <Button
                        onClick={() => router.push(`/dashboard/calendar-plans/${plan.id}`)}
                        variant="outline"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Просмотр
                      </Button>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

