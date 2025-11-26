'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { calendarPlansAPI } from '@/lib/api'
import { Calendar, ArrowLeft, Download, Building2, Stethoscope, Users, CalendarDays, Edit, Save, X } from 'lucide-react'
import { useUserStore } from '@/store/userStore'

export default function CalendarPlanDetailPage() {
  const router = useRouter()
  const params = useParams()
  const isAuthenticated = useIsAuthenticated()
  const [plan, setPlan] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [selectedView, setSelectedView] = useState<'calendar' | 'list'>('calendar')
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editedPlanData, setEditedPlanData] = useState<any>({})
  const { profile } = useUserStore()
  
  // Проверяем, может ли пользователь редактировать план (только клиника)
  const canEdit = plan && profile?.organizations?.some((o: any) => o.type === 'clinic' && o.id === plan.clinic)
  
  // Используем editedPlanData в режиме редактирования
  const currentPlanData = isEditing ? editedPlanData : (plan?.plan_data || {})

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    loadPlan()
  }, [isAuthenticated, router, params.id])

  const loadPlan = async () => {
    try {
      const response = await calendarPlansAPI.get(Number(params.id))
      setPlan(response.data)
      
      // Устанавливаем первую дату по умолчанию
      const planData = response.data.plan_data || {}
      const dates = Object.keys(planData).sort()
      if (dates.length > 0) {
        setSelectedDate(dates[0])
      }
      
      // Инициализируем editedPlanData
      setEditedPlanData(JSON.parse(JSON.stringify(planData)))
    } catch (error: any) {
      console.error('Ошибка загрузки плана:', error)
      if (error.response?.status === 404) {
        router.push('/dashboard/calendar-plans')
      }
    } finally {
      setLoading(false)
    }
  }

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

  const formatDateFull = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    } catch {
      return dateStr
    }
  }

  const getWeekDates = () => {
    if (!plan || !selectedDate) return []
    
    const currentData = isEditing ? editedPlanData : plan.plan_data || {}
    const dates = Object.keys(currentData).sort()
    const selectedIndex = dates.indexOf(selectedDate)
    
    if (selectedIndex === -1) return dates.slice(0, 7)
    
    // Показываем неделю вокруг выбранной даты
    const start = Math.max(0, selectedIndex - 3)
    const end = Math.min(dates.length, start + 7)
    return dates.slice(start, end)
  }

  const getMonthDates = () => {
    if (!plan) return []
    
    const currentData = isEditing ? editedPlanData : plan.plan_data || {}
    const dates = Object.keys(currentData).sort()
    if (dates.length === 0) return []
    
    // Группируем по месяцам
    const months: { [key: string]: string[] } = {}
    
    dates.forEach(dateStr => {
      const date = new Date(dateStr)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      
      if (!months[monthKey]) {
        months[monthKey] = []
      }
      months[monthKey].push(dateStr)
    })
    
    return months
  }

  const handleExportPDF = () => {
    // TODO: Реализовать экспорт в PDF
    alert('Экспорт в PDF будет реализован в ближайшее время')
  }

  const handleExportExcel = () => {
    // TODO: Реализовать экспорт в Excel
    alert('Экспорт в Excel будет реализован в ближайшее время')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка календарного плана...</p>
        </div>
      </div>
    )
  }

  if (!plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Календарный план не найден</p>
            <Button onClick={() => router.push('/dashboard/calendar-plans')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Вернуться к списку
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  const planData = plan?.plan_data || {}
  const dates = Object.keys(currentPlanData).sort()
  const weekDates = getWeekDates()
  const monthDates = getMonthDates()

  const stats = {
    totalDates: dates.length,
    totalEmployees: dates.reduce((sum, date) => sum + (currentPlanData[date]?.length || 0), 0),
    startDate: dates.length > 0 ? dates[0] : null,
    endDate: dates.length > 0 ? dates[dates.length - 1] : null,
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="outline"
            onClick={() => router.push('/dashboard/calendar-plans')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад к списку
          </Button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Calendar className="w-8 h-8" />
                Календарный план на {plan.year} год
              </h1>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Работодатель</p>
                    <p className="font-medium">{plan.employer_name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Stethoscope className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Клиника</p>
                    <p className="font-medium">{plan.clinic_name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <CalendarDays className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Период</p>
                    {stats.startDate && stats.endDate && (
                      <p className="font-medium">
                        {formatDate(stats.startDate)} - {formatDate(stats.endDate)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              {canEdit && !isEditing && (
                <Button variant="outline" onClick={() => {
                  setIsEditing(true)
                  setEditedPlanData(JSON.parse(JSON.stringify(plan.plan_data || {})))
                }}>
                  <Edit className="w-4 h-4 mr-2" />
                  Редактировать
                </Button>
              )}
              {isEditing && (
                <>
                  <Button variant="outline" onClick={async () => {
                    try {
                      await calendarPlansAPI.partialUpdate(plan.id, { plan_data: editedPlanData })
                      setPlan({ ...plan, plan_data: editedPlanData })
                      setIsEditing(false)
                      alert('Календарный план успешно обновлен!')
                    } catch (error: any) {
                      alert('Ошибка обновления плана: ' + (error.response?.data?.error || 'Неизвестная ошибка'))
                    }
                  }}>
                    <Save className="w-4 h-4 mr-2" />
                    Сохранить
                  </Button>
                  <Button variant="outline" onClick={() => {
                    setIsEditing(false)
                    setEditedPlanData(JSON.parse(JSON.stringify(plan.plan_data || {})))
                  }}>
                    <X className="w-4 h-4 mr-2" />
                    Отмена
                  </Button>
                </>
              )}
              <Button variant="outline" onClick={handleExportExcel}>
                <Download className="w-4 h-4 mr-2" />
                Excel
              </Button>
              <Button variant="outline" onClick={handleExportPDF}>
                <Download className="w-4 h-4 mr-2" />
                PDF
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-6 grid grid-cols-3 gap-4">
            <Card>
              <div className="text-center py-4">
                <p className="text-2xl font-bold text-primary-600">{stats.totalDates}</p>
                <p className="text-sm text-gray-600 mt-1">Всего дней</p>
              </div>
            </Card>
            <Card>
              <div className="text-center py-4">
                <p className="text-2xl font-bold text-primary-600">{stats.totalEmployees}</p>
                <p className="text-sm text-gray-600 mt-1">Всего сотрудников</p>
              </div>
            </Card>
            <Card>
              <div className="text-center py-4">
                <p className="text-2xl font-bold text-primary-600">
                  {stats.totalDates > 0 ? Math.ceil(stats.totalEmployees / stats.totalDates) : 0}
                </p>
                <p className="text-sm text-gray-600 mt-1">Среднее в день</p>
              </div>
            </Card>
          </div>
        </div>

        {/* View Toggle */}
        <div className="mb-6 flex gap-2">
          <Button
            variant={selectedView === 'calendar' ? 'default' : 'outline'}
            onClick={() => setSelectedView('calendar')}
          >
            <Calendar className="w-4 h-4 mr-2" />
            Календарь
          </Button>
          <Button
            variant={selectedView === 'list' ? 'default' : 'outline'}
            onClick={() => setSelectedView('list')}
          >
            <Users className="w-4 h-4 mr-2" />
            Список
          </Button>
        </div>

        {/* Calendar View */}
        {selectedView === 'calendar' && (
          <div className="space-y-6">
            {/* Month Overview */}
            {Object.entries(monthDates).map(([monthKey, monthDatesList]) => {
              const [year, month] = monthKey.split('-')
              const monthName = new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString('ru-RU', {
                month: 'long',
                year: 'numeric'
              })
              
              return (
                <Card key={monthKey} className="overflow-hidden">
                  <div className="bg-primary-600 text-white px-6 py-4">
                    <h3 className="text-xl font-semibold capitalize">{monthName}</h3>
                  </div>
                  
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {monthDatesList.map((dateStr) => {
                        const employees = currentPlanData[dateStr] || []
                        const isSelected = selectedDate === dateStr
                        
                        return (
                          <div
                            key={dateStr}
                            onClick={() => setSelectedDate(dateStr)}
                            className={`
                              p-4 border-2 rounded-lg cursor-pointer transition-all
                              ${isSelected 
                                ? 'border-primary-600 bg-primary-50' 
                                : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                              }
                            `}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <p className="font-semibold text-gray-900">
                                {formatDate(dateStr)}
                              </p>
                              <span className={`
                                px-2 py-1 rounded text-xs font-medium
                                ${isSelected 
                                  ? 'bg-primary-600 text-white' 
                                  : 'bg-gray-100 text-gray-700'
                                }
                              `}>
                                {employees.length} чел.
                              </span>
                            </div>
                            {employees.length > 0 && (
                              <div className="mt-2 space-y-1">
                                {employees.slice(0, 3).map((emp: any, idx: number) => (
                                  <p key={idx} className="text-sm text-gray-600 truncate">
                                    {emp.full_name}
                                  </p>
                                ))}
                                {employees.length > 3 && (
                                  <p className="text-xs text-gray-400">
                                    и еще {employees.length - 3}...
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        )}

        {/* List View */}
        {selectedView === 'list' && (
          <div className="space-y-4">
            {dates.map((dateStr) => {
              const employees = currentPlanData[dateStr] || []
              
              return (
                <Card key={dateStr}>
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {formatDateFull(dateStr)}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Запланировано осмотров: {employees.length}
                        </p>
                      </div>
                      <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                        {employees.length} чел.
                      </span>
                    </div>
                    
                    {employees.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {employees.map((emp: any, idx: number) => (
                          <div
                            key={idx}
                            className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                          >
                            <p className="font-medium text-gray-900">{emp.full_name}</p>
                            {emp.position && (
                              <p className="text-sm text-gray-600 mt-1">{emp.position}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center py-4">Нет запланированных осмотров</p>
                    )}
                  </div>
                </Card>
              )
            })}
          </div>
        )}

        {/* Selected Date Details */}
        {selectedDate && currentPlanData[selectedDate] && selectedView === 'calendar' && (
          <Card className="mt-6">
            <div className="p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                {formatDateFull(selectedDate)}
                {isEditing && (
                  <span className="ml-2 text-sm text-primary-600 font-normal">(Режим редактирования)</span>
                )}
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {currentPlanData[selectedDate].map((emp: any, idx: number) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg border ${
                      isEditing 
                        ? 'bg-white border-primary-300 hover:border-primary-500 cursor-move' 
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <p className="font-medium text-gray-900">{emp.full_name}</p>
                    {emp.position && (
                      <p className="text-sm text-gray-600 mt-1">{emp.position}</p>
                    )}
                    {isEditing && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-2 w-full"
                        onClick={() => {
                          // Удаляем сотрудника из текущей даты
                          const newPlanData = { ...editedPlanData }
                          if (!newPlanData[selectedDate]) {
                            newPlanData[selectedDate] = []
                          }
                          newPlanData[selectedDate] = newPlanData[selectedDate].filter((e: any) => 
                            e.employee_id !== emp.employee_id
                          )
                          setEditedPlanData(newPlanData)
                        }}
                      >
                        Удалить
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              
              {isEditing && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800 mb-2">
                    💡 Для перемещения сотрудника на другую дату: удалите его здесь, затем выберите нужную дату и добавьте его вручную.
                  </p>
                  <p className="text-xs text-blue-600">
                    Примечание: Полное редактирование с drag-and-drop будет добавлено в следующей версии.
                  </p>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}

