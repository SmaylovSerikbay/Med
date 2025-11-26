'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { organizationsAPI, subscriptionsAPI, examinationsAPI } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Loading } from '@/components/ui/Loading'
import { 
  Users, 
  Calendar, 
  FileText, 
  Building2,
  Stethoscope,
  QrCode,
  UserCheck,
  CreditCard,
  AlertCircle,
  UserPlus,
  TrendingUp,
  Activity,
  ArrowRight,
  Sparkles,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react'

// Компонент объединенного дашборда для пациента
function PatientDashboard({ profile, employee, fullName, router }: any) {
  const [examinations, setExaminations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'scheduled' | 'in_progress' | 'completed'>('all')

  useEffect(() => {
    loadExaminations()
  }, [])

  const loadExaminations = async () => {
    try {
      const response = await examinationsAPI.list()
      setExaminations(response.data.results || response.data)
    } catch (error) {
      console.error('Ошибка загрузки осмотров:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredExaminations = filter === 'all'
    ? examinations
    : examinations.filter((e) => e.status === filter)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'in_progress':
        return <Clock className="w-5 h-5 text-blue-600" />
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <Calendar className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50/50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        {/* Header Section */}
        <div className="mb-8 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl shadow-lg">
              <UserCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">Мой профиль</h1>
              <p className="text-gray-500 mt-1">Медицинские осмотры и результаты</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Информация о пациенте */}
          <Card variant="elevated" className="border-0 animate-slide-up h-fit">
            <div className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl">
                  <UserCheck className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Информация</h2>
                  <p className="text-sm text-gray-500">Ваши данные</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">ФИО</p>
                  <p className="text-lg font-semibold text-gray-900">{fullName}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Телефон</p>
                  <p className="text-lg font-semibold text-gray-900">{profile.user.phone_number}</p>
                </div>
                {employee && (
                  <>
                    {employee.iin && (
                      <div>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">ИИН</p>
                        <p className="text-lg font-semibold text-gray-900">{employee.iin}</p>
                      </div>
                    )}
                    {employee.position_name && (
                      <div>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Должность</p>
                        <p className="text-lg font-semibold text-gray-900">{employee.position_name}</p>
                      </div>
                    )}
                    {employee.department && (
                      <div>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Отдел/Цех</p>
                        <p className="text-lg font-semibold text-gray-900">{employee.department}</p>
                      </div>
                    )}
                    {employee.employer_name && (
                      <div>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Работодатель</p>
                        <p className="text-lg font-semibold text-gray-900">{employee.employer_name}</p>
                      </div>
                    )}
                    {employee.hire_date && (
                      <div>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Дата приема</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {new Date(employee.hire_date).toLocaleDateString('ru-RU')}
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </Card>

          {/* Список осмотров */}
          <div className="lg:col-span-2 space-y-6">
            <Card variant="elevated" className="border-0 animate-slide-up" style={{ animationDelay: '100ms' }}>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-900">Мои осмотры</h2>
                    <p className="text-sm text-gray-500 mt-1">История медицинских осмотров</p>
                  </div>
                  <div className="p-3 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl">
                    <Stethoscope className="w-6 h-6 text-white" />
                  </div>
                </div>

                {/* Фильтры */}
                <div className="flex gap-2 mb-6 flex-wrap">
                  {(['all', 'scheduled', 'in_progress', 'completed'] as const).map((f) => (
                    <Button
                      key={f}
                      variant={filter === f ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setFilter(f)}
                    >
                      {f === 'all' ? 'Все' :
                       f === 'scheduled' ? 'Запланированные' :
                       f === 'in_progress' ? 'В процессе' :
                       'Завершенные'}
                    </Button>
                  ))}
                </div>

                {/* Список осмотров */}
                {loading ? (
                  <div className="text-center py-12">
                    <Loading />
                  </div>
                ) : filteredExaminations.length === 0 ? (
                  <div className="text-center py-12">
                    <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Нет осмотров</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filteredExaminations.map((exam: any) => (
                      <Card
                        key={exam.id}
                        variant="default"
                        className="hover:shadow-lg transition-all cursor-pointer border border-gray-200"
                        onClick={() => router.push(`/dashboard/examinations/${exam.id}`)}
                      >
                        <div className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3 flex-1">
                              {getStatusIcon(exam.status)}
                              <div className="flex-1">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {exam.clinic_name || 'Клиника не указана'}
                                </h3>
                                <p className="text-sm text-gray-500">
                                  {exam.scheduled_date ? new Date(exam.scheduled_date).toLocaleDateString('ru-RU') : 'Дата не указана'}
                                </p>
                              </div>
                              <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(exam.status)}`}>
                                {exam.status === 'scheduled' ? 'Запланирован' :
                                 exam.status === 'in_progress' ? 'В процессе' :
                                 exam.status === 'completed' ? 'Завершен' :
                                 'Отменен'}
                              </span>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            {exam.result && (
                              <div>
                                <span className="font-medium text-gray-900">Результат:</span>{' '}
                                {exam.result === 'fit' ? 'Годен' :
                                 exam.result === 'unfit' ? 'Не годен' :
                                 'С ограничениями'}
                              </div>
                            )}
                          </div>
                          {exam.progress && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <div className="flex justify-between text-sm mb-2">
                                <span className="text-gray-600">Прогресс осмотра</span>
                                <span className="font-medium text-gray-900">
                                  {exam.progress.completed_exams} / {exam.progress.total_doctors}
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-gradient-to-r from-emerald-500 to-emerald-600 h-2 rounded-full transition-all"
                                  style={{ width: `${exam.progress.progress_percent}%` }}
                                ></div>
                              </div>
                            </div>
                          )}
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}

// Компонент объединенного дашборда для врача
function DoctorDashboard({ profile, clinicOrgs, roleLabel, fullName, router }: any) {
  const [examinations, setExaminations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'scheduled' | 'in_progress' | 'completed'>('all')

  useEffect(() => {
    loadExaminations()
  }, [])

  const loadExaminations = async () => {
    try {
      const response = await examinationsAPI.list()
      setExaminations(response.data.results || response.data)
    } catch (error) {
      console.error('Ошибка загрузки осмотров:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredExaminations = filter === 'all'
    ? examinations
    : examinations.filter((e) => e.status === filter)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'in_progress':
        return <Clock className="w-5 h-5 text-blue-600" />
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <Calendar className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50/50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        {/* Header Section */}
        <div className="mb-8 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl shadow-lg">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">Дашборд {roleLabel}</h1>
              <p className="text-gray-500 mt-1">Медицинские осмотры</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Информация о враче */}
          <Card variant="elevated" className="border-0 animate-slide-up h-fit">
            <div className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl">
                  <UserCheck className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Информация</h2>
                  <p className="text-sm text-gray-500">Ваши данные</p>
                </div>
              </div>
              <div className="space-y-4">
                {clinicOrgs.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Клиника</p>
                    <p className="text-lg font-semibold text-gray-900">{clinicOrgs.map((o: any) => o.name).join(', ')}</p>
                  </div>
                )}
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">ФИО</p>
                  <p className="text-lg font-semibold text-gray-900">{fullName}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Телефон</p>
                  <p className="text-lg font-semibold text-gray-900">{profile.user.phone_number}</p>
                </div>
                {profile.medical_staff?.specialization && (
                  <div>
                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Специализация</p>
                    <p className="text-lg font-semibold text-gray-900">{profile.medical_staff.specialization}</p>
                  </div>
                )}
                {profile.medical_staff?.license_number && (
                  <div>
                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Лицензия</p>
                    <p className="text-lg font-semibold text-gray-900">{profile.medical_staff.license_number}</p>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Список осмотров */}
          <div className="lg:col-span-2 space-y-6">
            <Card variant="elevated" className="border-0 animate-slide-up" style={{ animationDelay: '100ms' }}>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-900">Мои осмотры</h2>
                    <p className="text-sm text-gray-500 mt-1">Ваши назначенные осмотры</p>
                  </div>
                  <div className="p-3 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl">
                    <Stethoscope className="w-6 h-6 text-white" />
                  </div>
                </div>

                {/* Фильтры */}
                <div className="flex gap-2 mb-6 flex-wrap">
                  {(['all', 'scheduled', 'in_progress', 'completed'] as const).map((f) => (
                    <Button
                      key={f}
                      variant={filter === f ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setFilter(f)}
                    >
                      {f === 'all' ? 'Все' :
                       f === 'scheduled' ? 'Запланированные' :
                       f === 'in_progress' ? 'В процессе' :
                       'Завершенные'}
                    </Button>
                  ))}
                </div>

                {/* Список осмотров */}
                {loading ? (
                  <div className="text-center py-12">
                    <Loading />
                  </div>
                ) : filteredExaminations.length === 0 ? (
                  <div className="text-center py-12">
                    <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Нет осмотров</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filteredExaminations.map((exam: any) => (
                      <Card
                        key={exam.id}
                        variant="default"
                        className="hover:shadow-lg transition-all cursor-pointer border border-gray-200"
                        onClick={() => router.push(`/dashboard/examinations/${exam.id}`)}
                      >
                        <div className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3 flex-1">
                              {getStatusIcon(exam.status)}
                              <div className="flex-1">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {exam.employee_info?.full_name || 'Не указано'}
                                </h3>
                                <p className="text-sm text-gray-500">
                                  {exam.employee_info?.position_name || 'Без должности'}
                                </p>
                              </div>
                              <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(exam.status)}`}>
                                {exam.status === 'scheduled' ? 'Запланирован' :
                                 exam.status === 'in_progress' ? 'В процессе' :
                                 exam.status === 'completed' ? 'Завершен' :
                                 'Отменен'}
                              </span>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            <div>
                              <span className="font-medium text-gray-900">Клиника:</span>{' '}
                              {exam.clinic_name || 'Не указано'}
                            </div>
                            <div>
                              <span className="font-medium text-gray-900">Дата:</span>{' '}
                              {exam.scheduled_date ? new Date(exam.scheduled_date).toLocaleDateString('ru-RU') : 'Не указано'}
                            </div>
                            {exam.result && (
                              <div>
                                <span className="font-medium text-gray-900">Результат:</span>{' '}
                                {exam.result === 'fit' ? 'Годен' :
                                 exam.result === 'unfit' ? 'Не годен' :
                                 'С ограничениями'}
                              </div>
                            )}
                          </div>
                          {exam.progress && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <div className="flex justify-between text-sm mb-2">
                                <span className="text-gray-600">Прогресс осмотра</span>
                                <span className="font-medium text-gray-900">
                                  {exam.progress.completed_exams} / {exam.progress.total_doctors}
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-gradient-to-r from-emerald-500 to-emerald-600 h-2 rounded-full transition-all"
                                  style={{ width: `${exam.progress.progress_percent}%` }}
                                ></div>
                              </div>
                            </div>
                          )}
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function DashboardPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const { profile, loadProfile, isLoading } = useUserStore()
  const [loading, setLoading] = useState(true)
  const [hasActiveSubscription, setHasActiveSubscription] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    
    if (!profile) {
      loadProfile().finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [isAuthenticated, router, profile, loadProfile])

  useEffect(() => {
    if (!profile) {
      setHasActiveSubscription(false)
      return
    }
    
    if (profile.organizations && profile.organizations.length > 0) {
      subscriptionsAPI.getCurrent()
        .then((res: any) => {
          const subs = res.data.results || res.data
          const active = Array.isArray(subs) && subs.some((s: any) => s.is_active)
          setHasActiveSubscription(active)
        })
        .catch(() => setHasActiveSubscription(false))
    } else {
      setHasActiveSubscription(false)
    }
  }, [profile])

  if (!isAuthenticated || loading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-6">Ошибка загрузки профиля</p>
            <Button onClick={loadProfile}>Попробовать снова</Button>
          </div>
        </Card>
      </div>
    )
  }

  const { primary_role, organizations } = profile
  const safeOrganizations = (organizations && Array.isArray(organizations)) ? organizations : []

  // Дашборд для Работодателя
  if (primary_role === 'employer') {
    const employerOrgs = safeOrganizations.filter((o: any) => o.type === 'employer')
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50/50">
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
          {/* Header Section */}
          <div className="mb-10 animate-fade-in">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg">
                <Building2 className="w-6 h-6 text-white" />
              </div>
            <div>
                <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">Дашборд Работодателя</h1>
                <p className="text-gray-500 mt-1">Управление сотрудниками и медицинскими осмотрами</p>
                </div>
            </div>
            {employerOrgs.length > 0 && (
              <div className="mt-4 flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-200/60 w-fit">
                <Building2 className="w-4 h-4 text-primary-600" />
                <span className="text-sm font-medium text-gray-700">
                  Организации: <span className="text-primary-600">{employerOrgs.map(o => o.name).join(', ')}</span>
                </span>
              </div>
            )}
        </div>

          {/* Actions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
            <Card 
              variant="elevated"
              className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
              style={{ animationDelay: '0ms' }}
              onClick={() => router.push('/dashboard/employees')}
            >
              <div className="p-6">
                <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                  <Users className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Сотрудники</h3>
                <p className="text-gray-500 text-sm mb-6">Управление сотрудниками организации</p>
                <div className="flex items-center text-primary-600 font-medium text-sm group-hover:gap-3 transition-all">
                  Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Card>

            <Card 
              variant="elevated"
              className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
              style={{ animationDelay: '100ms' }}
              onClick={() => router.push('/dashboard/examinations')}
            >
              <div className="p-6">
                <div className="p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                  <Stethoscope className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Осмотры</h3>
                <p className="text-gray-500 text-sm mb-6">Просмотр осмотров сотрудников</p>
                <div className="flex items-center text-emerald-600 font-medium text-sm group-hover:gap-3 transition-all">
                  Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Card>

            <Card 
              variant="elevated"
              className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
              style={{ animationDelay: '200ms' }}
              onClick={() => router.push('/dashboard/calendar-plans')}
            >
              <div className="p-6">
                <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                  <Calendar className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Календарные планы</h3>
                <p className="text-gray-500 text-sm mb-6">Просмотр и управление планами осмотров</p>
                <div className="flex items-center text-purple-600 font-medium text-sm group-hover:gap-3 transition-all">
                  Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Card>

            <Card 
              variant="elevated"
              className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
              style={{ animationDelay: '300ms' }}
              onClick={() => router.push('/dashboard/subscriptions')}
            >
              <div className="p-6">
                <div className="p-4 bg-gradient-to-br from-amber-50 to-amber-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                  <CreditCard className="w-8 h-8 text-amber-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Подписки</h3>
                <p className="text-gray-500 text-sm mb-6">Управление подписками организации</p>
                <div className="flex items-center text-amber-600 font-medium text-sm group-hover:gap-3 transition-all">
                  Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Card>
          </div>
        </main>
      </div>
    )
  }

  // Дашборд для Клиники
  if (primary_role === 'clinic') {
    const clinicOrgs = safeOrganizations.filter((o: any) => o.type === 'clinic')
    const isClinicOwner = profile.roles.includes('clinic_owner')
    const userClinicRole = clinicOrgs.find(o => o.role)?.role || 'doctor'
    
    const roleLabels: Record<string, string> = {
      'doctor': 'Врач',
      'registrar': 'Регистратор',
      'profpathologist': 'Профпатолог',
      'admin': 'Администратор',
    }
    const roleLabel = roleLabels[userClinicRole] || 'Медработник'
    
    const fullName = [profile.user.last_name, profile.user.first_name, profile.user.middle_name]
      .filter(Boolean).join(' ') || 'Не указано'
    
    // Для обычного врача показываем объединенный дашборд
    const isRegularDoctor = userClinicRole === 'doctor' && !isClinicOwner
    
    // Если это обычный врач, показываем объединенный дашборд
    if (isRegularDoctor) {
      return <DoctorDashboard profile={profile} clinicOrgs={clinicOrgs} roleLabel={roleLabel} fullName={fullName} router={router} />
    }
    
    // Для владельца клиники и регистратора показываем стандартный дашборд
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50/50">
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
          {/* Header Section */}
          <div className="mb-10 animate-fade-in">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl shadow-lg">
                <Stethoscope className="w-6 h-6 text-white" />
              </div>
            <div>
                <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">
                {isClinicOwner ? 'Дашборд Клиники' : `Дашборд ${roleLabel}`}
              </h1>
                <p className="text-gray-500 mt-1">
                  {isClinicOwner ? 'Управление медицинскими осмотрами' : 'Работа с медицинскими осмотрами'}
              </p>
              </div>
            </div>
              {clinicOrgs.length > 0 && (
              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-200/60 w-fit">
                  <Stethoscope className="w-4 h-4 text-primary-600" />
                  <span className="text-sm font-medium text-gray-700">
                    Клиника: <span className="text-primary-600">{clinicOrgs.map(o => o.name).join(', ')}</span>
                    {!isClinicOwner && <span className="text-gray-500 ml-2">• {roleLabel}</span>}
                  </span>
                </div>
                {(profile.user.first_name || profile.user.last_name || profile.medical_staff?.specialization) && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-200/60 w-fit">
                    <span className="text-sm font-medium text-gray-700">
                      {fullName}
                      {profile.medical_staff?.specialization && (
                        <span className="text-gray-500 ml-2">• {profile.medical_staff.specialization}</span>
                      )}
                    </span>
                  </div>
                  )}
                </div>
              )}
        </div>

          {/* Actions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
            {(userClinicRole === 'registrar' || isClinicOwner) && (
              <Card 
                variant="elevated"
                className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
                onClick={() => router.push('/dashboard/clinic/registry')}
              >
                <div className="p-6">
                  <div className="p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                    <QrCode className="w-8 h-8 text-indigo-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Регистратура</h3>
                  <p className="text-gray-500 text-sm mb-6">Сканирование QR-кодов и начало осмотров</p>
                  <div className="flex items-center text-indigo-600 font-medium text-sm group-hover:gap-3 transition-all">
                    Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Card>
            )}

            <Card 
              variant="elevated"
              className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
              onClick={() => router.push('/dashboard/examinations')}
            >
              <div className="p-6">
                <div className="p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                  <Stethoscope className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Осмотры</h3>
                <p className="text-gray-500 text-sm mb-6">
                  {isClinicOwner ? 'Просмотр всех осмотров в клинике' : 'Ваши назначенные осмотры'}
                </p>
                <div className="flex items-center text-emerald-600 font-medium text-sm group-hover:gap-3 transition-all">
                  Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Card>

            {isClinicOwner && (
              <>
                <Card 
                  variant="elevated"
                  className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
                  onClick={() => router.push('/dashboard/documents')}
                >
                  <div className="p-6">
                    <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                      <FileText className="w-8 h-8 text-purple-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Документы</h3>
                    <p className="text-gray-500 text-sm mb-6">Генерация документов согласно Приказу 131</p>
                    <div className="flex items-center text-purple-600 font-medium text-sm group-hover:gap-3 transition-all">
                      Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Card>

                <Card 
                  variant="elevated"
                  className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
                  onClick={() => router.push('/dashboard/clinic/staff')}
                >
                  <div className="p-6">
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                      <Users className="w-8 h-8 text-blue-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Медработники</h3>
                    <p className="text-gray-500 text-sm mb-6">Управление врачами и регистраторами</p>
                    <div className="flex items-center text-blue-600 font-medium text-sm group-hover:gap-3 transition-all">
                      Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Card>

                <Card 
                  variant="elevated"
                  className="group cursor-pointer hover:shadow-xl transition-all duration-300 border-0 animate-scale-in"
                  onClick={() => router.push('/dashboard/subscriptions')}
                >
                  <div className="p-6">
                    <div className="p-4 bg-gradient-to-br from-amber-50 to-amber-100 rounded-2xl mb-4 w-fit group-hover:scale-110 transition-transform duration-300">
                      <CreditCard className="w-8 h-8 text-amber-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Подписки</h3>
                    <p className="text-gray-500 text-sm mb-6">Управление подписками клиники</p>
                    <div className="flex items-center text-amber-600 font-medium text-sm group-hover:gap-3 transition-all">
                      Перейти <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Card>
              </>
            )}
          </div>
        </main>
      </div>
    )
  }

  // Дашборд для Пациента (сотрудника)
  const isPatient = primary_role === 'patient' || profile.roles.includes('patient')
  
  if (isPatient) {
    const employee = profile.employee
    const fullName = employee 
      ? [employee.last_name, employee.first_name, employee.middle_name].filter(Boolean).join(' ')
      : [profile.user.last_name, profile.user.first_name, profile.user.middle_name].filter(Boolean).join(' ') || 'Не указано'
    
    return <PatientDashboard profile={profile} employee={employee} fullName={fullName} router={router} />
  }

  // Дашборд для нового пользователя без организаций
  const hasOrganizations = safeOrganizations && safeOrganizations.length > 0
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50/50">
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="text-center mb-10 animate-fade-in">
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-3">Добро пожаловать!</h1>
          <p className="text-gray-500 text-lg">Создайте организацию чтобы начать работу с платформой</p>
      </div>

      {!hasOrganizations && (
          <Card variant="elevated" className="border-0 max-w-2xl mx-auto animate-scale-in">
            <div className="p-8 lg:p-12 text-center">
              <div className="p-4 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl w-fit mx-auto mb-6">
                <Building2 className="w-12 h-12 text-white" />
            </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">Создайте организацию</h2>
              <p className="text-gray-500 mb-8 max-w-md mx-auto">
                Выберите тип организации чтобы начать работу с платформой
            </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
              <Button
                onClick={() => router.push('/dashboard/organizations?create=employer')}
                  className="min-w-[200px]"
              >
                <Building2 className="w-4 h-4 mr-2" />
                Создать Работодателя
              </Button>
              <Button
                variant="outline"
                onClick={() => router.push('/dashboard/organizations?create=clinic')}
                  className="min-w-[200px]"
              >
                <Stethoscope className="w-4 h-4 mr-2" />
                Создать Клинику
              </Button>
            </div>
              <p className="text-sm text-gray-400">
                После создания организации вам нужно будет запросить подписку для доступа к функциям
              </p>
          </div>
        </Card>
      )}
      </main>
    </div>
  )
}
