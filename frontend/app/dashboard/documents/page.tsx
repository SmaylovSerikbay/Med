'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { documentsAPI, organizationsAPI, partnershipsAPI, calendarPlansAPI } from '@/lib/api'
import { FileText, Download, CheckCircle, Clock } from 'lucide-react'

export default function DocumentsPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const [documents, setDocuments] = useState<any[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])
  const [partnerEmployers, setPartnerEmployers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingEmployers, setLoadingEmployers] = useState(false)
  const [showGenerateForm, setShowGenerateForm] = useState(false)
  const [generateType, setGenerateType] = useState<'appendix3' | 'calendar' | 'final_act' | null>(null)
  const { profile } = useUserStore()
  const userClinic = profile?.organizations?.find((o: any) => o.type === 'clinic')
  
  const [formData, setFormData] = useState({
    employer_id: '',
    clinic_id: '',
    year: new Date().getFullYear(),
    start_date: '',
    end_date: '', // Конечная дата для календарного плана
  })

  // Обновляем clinic_id когда загрузится профиль
  useEffect(() => {
    if (profile?.organizations) {
      const clinic = profile.organizations.find((o: any) => o.type === 'clinic')
      if (clinic) {
        setFormData(prev => ({ ...prev, clinic_id: clinic.id }))
      }
    }
  }, [profile])

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    
    // Документы могут просматривать и клиники, и работодатели
    // Генерировать могут только клиники
    const { profile, loadProfile } = useUserStore.getState()
    if (!profile) {
      loadProfile().then(() => {
        loadData()
      })
    } else {
      loadData()
    }
  }, [isAuthenticated, router])

  const loadPartnerEmployers = async () => {
    setLoadingEmployers(true)
    try {
      const response = await partnershipsAPI.partnerEmployers()
      setPartnerEmployers(response.data || [])
      console.log('Загружены работодатели-партнеры:', response.data?.length || 0, response.data)
    } catch (error: any) {
      console.error('Ошибка загрузки работодателей-партнеров:', error)
      // Fallback: пробуем получить из общего списка партнерств
      try {
        const partnershipsRes = await partnershipsAPI.list()
        const partnerships = partnershipsRes.data.results || partnershipsRes.data
        const activePartnershipEmployerIds = partnerships
          .filter((p: any) => p.status === 'active' && p.clinic === userClinic?.id)
          .map((p: any) => p.employer)
        
        // Находим работодателей в общем списке организаций
        const employers = organizations.filter(
          (o: any) => o.org_type === 'employer' && activePartnershipEmployerIds.includes(o.id)
        )
        setPartnerEmployers(employers)
      } catch (fallbackError) {
        console.error('Ошибка fallback загрузки работодателей:', fallbackError)
        setPartnerEmployers([])
      }
    } finally {
      setLoadingEmployers(false)
    }
  }

  const loadData = async () => {
    try {
      const [docsRes, orgsRes] = await Promise.all([
        documentsAPI.list(),
        organizationsAPI.list(),
      ])
      setDocuments(docsRes.data.results || docsRes.data)
      const allOrgs = orgsRes.data.results || orgsRes.data
      setOrganizations(allOrgs)
      // Устанавливаем клинику в formData если еще не установлена
      if (!formData.clinic_id && userClinic) {
        setFormData(prev => ({ ...prev, clinic_id: userClinic.id }))
      }
      
      // Загружаем работодателей с активными партнерствами для клиники
      if (userClinic) {
        await loadPartnerEmployers()
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const clinicId = userClinic?.id || formData.clinic_id
      // Приложение 3 теперь обновляется автоматически при изменении сотрудников
      // Эта функция больше не нужна, но оставляем для совместимости
      if (generateType === 'appendix3') {
        alert('Приложение 3 обновляется автоматически при добавлении или изменении сотрудников. Нет необходимости обновлять его вручную.')
        setShowGenerateForm(false)
        setGenerateType(null)
        await loadData()
        return
      } else if (generateType === 'calendar') {
        if (!formData.start_date || !formData.end_date) {
          alert('Укажите дату начала и дату окончания осмотров')
          return
        }
        try {
          const response = await documentsAPI.generateCalendarPlan(
            parseInt(formData.employer_id),
            parseInt(clinicId),
            formData.year,
            formData.start_date,
            formData.end_date
          )
          
          // Проверяем, был ли план создан или уже существовал
          if (response.data.id && response.data.message) {
            // План уже существует
            const confirmed = confirm(
              'Календарный план уже существует для этого работодателя и года. Хотите перейти к редактированию?'
            )
            if (confirmed) {
              router.push(`/dashboard/calendar-plans/${response.data.id}`)
            }
          } else {
            // План создан
            alert('Календарный план успешно создан! Теперь вы можете отредактировать его при необходимости.')
            await loadData()
            // Переходим к просмотру созданного плана
            if (response.data.id) {
              router.push(`/dashboard/calendar-plans/${response.data.id}`)
            } else {
              router.push('/dashboard/calendar-plans')
            }
          }
        } catch (error: any) {
          if (error.response?.status === 200 && error.response?.data?.id) {
            // План уже существует
            const confirmed = confirm(
              'Календарный план уже существует для этого работодателя и года. Хотите перейти к редактированию?'
            )
            if (confirmed) {
              router.push(`/dashboard/calendar-plans/${error.response.data.id}`)
            }
          } else {
            alert('Ошибка создания календарного плана: ' + (error.response?.data?.error || 'Неизвестная ошибка'))
          }
        }
      } else if (generateType === 'final_act') {
        await documentsAPI.generateFinalAct(
          parseInt(formData.employer_id),
          parseInt(clinicId),
          formData.year
        )
        alert('Заключительный акт успешно создан!')
        // Обновляем список документов
        await loadData()
      }
      setShowGenerateForm(false)
      setGenerateType(null)
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка генерации документа')
    }
  }

  const handleRequestSignature = async (docId: number, role: string) => {
    try {
      await documentsAPI.requestSignature(docId, role)
      alert('OTP код отправлен на WhatsApp для подписания')
      loadData()
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка запроса подписи')
    }
  }

  const handleSign = async (docId: number, role: string) => {
    const otpCode = prompt('Введите OTP код из WhatsApp:')
    if (!otpCode) return

    try {
      await documentsAPI.verifyAndSign(docId, role, otpCode)
      alert('Документ успешно подписан!')
      loadData()
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка подписания')
    }
  }

  // Используем работодателей с активными партнерствами для клиники
  // Если список пуст, используем всех работодателей (fallback)
  const employers = partnerEmployers.length > 0 
    ? partnerEmployers 
    : organizations.filter((o) => o.org_type === 'employer')
  const clinics = organizations.filter((o) => o.org_type === 'clinic')

  if (!isAuthenticated) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Документы</h1>
            <p className="text-gray-600 mt-2">
              {userClinic && profile?.roles?.includes('clinic_owner') 
                ? 'Генерация документов согласно Приказу 131. Приложение 3 обновляется автоматически при изменении сотрудников.' 
                : 'Просмотр документов согласно Приказу 131. Приложение 3 обновляется автоматически при изменении сотрудников.'}
            </p>
          </div>
          {/* Кнопки генерации доступны только клиникам */}
          {userClinic && profile?.roles?.includes('clinic_owner') && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setGenerateType('calendar')
                  setShowGenerateForm(true)
                  if (userClinic) {
                    loadPartnerEmployers()
                  }
                }}
              >
                Создать Календарный план
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setGenerateType('final_act')
                  setShowGenerateForm(true)
                  if (userClinic) {
                    loadPartnerEmployers()
                  }
                }}
              >
                Заключительный акт
              </Button>
            </div>
          )}
        </div>

        {showGenerateForm && (
          <Card className="mb-6">
            <h2 className="text-xl font-semibold mb-4">
              {generateType === 'calendar' && 'Создание Календарного плана'}
              {generateType === 'final_act' && 'Генерация Заключительного акта'}
            </h2>
            {generateType === 'calendar' && (
              <p className="text-sm text-gray-600 mb-4">
                Выберите диапазон дат (дату начала и дату окончания) для проведения осмотров. Система автоматически распределит сотрудников из Приложения 3 по датам с учетом пропускной способности клиники. После создания вы сможете отредактировать план вручную.
              </p>
            )}
            <form onSubmit={handleGenerate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Работодатель *
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    value={formData.employer_id}
                    onChange={(e) => setFormData({ ...formData, employer_id: e.target.value })}
                    required
                  >
                    <option value="">Выберите работодателя</option>
                    {loadingEmployers ? (
                      <option disabled>Загрузка работодателей...</option>
                    ) : employers.length === 0 ? (
                      <option disabled>
                        Нет работодателей с активными партнерствами. Сначала установите партнерство в разделе "Партнерства".
                      </option>
                    ) : (
                      employers.map((org) => (
                        <option key={org.id} value={org.id}>{org.name}</option>
                      ))
                    )}
                  </select>
                </div>
                {userClinic && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Клиника
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                      value={userClinic.name}
                      disabled
                      readOnly
                    />
                  </div>
                )}
                <Input
                  label="Год"
                  type="number"
                  value={formData.year}
                  onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
                  required
                />
                {generateType === 'calendar' && (
                  <>
                    <Input
                      label="Дата начала *"
                      type="date"
                      value={formData.start_date}
                      onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                      required
                    />
                    <Input
                      label="Дата окончания *"
                      type="date"
                      value={formData.end_date}
                      onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                      required
                      min={formData.start_date || undefined}
                    />
                  </>
                )}
              </div>
              <div className="flex gap-2">
                <Button type="submit">
                  {generateType === 'appendix3' ? 'Обновить' : 'Сгенерировать'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowGenerateForm(false)
                    setGenerateType(null)
                  }}
                >
                  Отмена
                </Button>
              </div>
            </form>
          </Card>
        )}

        {loading ? (
          <div className="text-center py-12">Загрузка...</div>
        ) : documents.length === 0 ? (
          <Card className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Нет документов</p>
          </Card>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <Card key={doc.id}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="w-6 h-6 text-primary-600" />
                      <h3 className="text-lg font-semibold">{doc.title}</h3>
                      <span className={`px-2 py-1 text-xs rounded ${
                        doc.status === 'signed' ? 'bg-green-100 text-green-800' :
                        doc.status === 'pending_signature' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {doc.status === 'signed' ? 'Подписан' :
                         doc.status === 'pending_signature' ? 'Ожидает подписи' :
                         'Черновик'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {doc.organization_name} • {doc.year} год
                    </p>
                    {doc.content && (
                      <div className="text-sm text-gray-500">
                        {doc.document_type === 'appendix_3' && (
                          <div className="flex items-center gap-4">
                            <p>Сотрудников: {doc.content.total_count || 0}</p>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => router.push(`/dashboard/documents/appendix3/${doc.id}`)}
                            >
                              <FileText className="w-4 h-4 mr-2" />
                              Просмотр в таблице
                            </Button>
                          </div>
                        )}
                        {doc.document_type === 'calendar_plan' && (
                          <div className="flex items-center gap-4">
                            <p>Период: {doc.content?.plan_data ? Object.keys(doc.content.plan_data).length + ' дней' : 'Не указан'}</p>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={async () => {
                                try {
                                  // Находим ID календарного плана по документу
                                  const response = await calendarPlansAPI.list()
                                  const plans = response.data.results || response.data || []
                                  const plan = plans.find((p: any) => p.document === doc.id || p.document_id === doc.id)
                                  if (plan) {
                                    router.push(`/dashboard/calendar-plans/${plan.id}`)
                                  } else {
                                    alert('Календарный план не найден. Возможно, он был удален.')
                                  }
                                } catch (error) {
                                  console.error('Ошибка загрузки календарного плана:', error)
                                  alert('Ошибка загрузки календарного плана')
                                }
                              }}
                            >
                              <FileText className="w-4 h-4 mr-2" />
                              Просмотр и редактирование
                            </Button>
                          </div>
                        )}
                        {doc.document_type === 'final_act' && doc.content.statistics && (
                          <div className="flex items-center gap-4">
                            <div className="flex gap-4">
                              <span>Осмотрено: {doc.content.statistics.total_examined}</span>
                              <span className="text-green-600">Годен: {doc.content.statistics.fit}</span>
                              <span className="text-red-600">Не годен: {doc.content.statistics.unfit}</span>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => router.push(`/dashboard/documents/final-act/${doc.id}`)}
                            >
                              <FileText className="w-4 h-4 mr-2" />
                              Просмотр и печать
                            </Button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {doc.signatures && doc.signatures.length > 0 && (
                      <div className="flex flex-col gap-1 mr-4">
                        {doc.signatures.map((sig: any) => (
                          <div key={sig.id} className="flex items-center gap-2 text-sm">
                            {sig.otp_verified ? (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : (
                              <Clock className="w-4 h-4 text-yellow-600" />
                            )}
                            <span className="text-gray-600">{sig.role}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {doc.status === 'pending_signature' && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRequestSignature(doc.id, 'clinic')}
                        >
                          Запросить подпись
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleSign(doc.id, 'clinic')}
                        >
                          Подписать
                        </Button>
                      </>
                    )}
                    {doc.file_path && (
                      <Button size="sm" variant="outline">
                        <Download className="w-4 h-4" />
                      </Button>
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

