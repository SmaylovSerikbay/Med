'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { examinationsAPI, organizationsAPI } from '@/lib/api'
import { CheckCircle, XCircle, AlertCircle, FileText } from 'lucide-react'

export default function ExaminationDetailPage() {
  const router = useRouter()
  const params = useParams()
  const isAuthenticated = useIsAuthenticated()
  const [examination, setExamination] = useState<any>(null)
  const [profpathologists, setProfpathologists] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [finalResult, setFinalResult] = useState('fit')
  const [showCompleteForm, setShowCompleteForm] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    loadData()
  }, [isAuthenticated, router, params.id])

  const loadData = async () => {
    try {
      const examRes = await examinationsAPI.get(Number(params.id))
      setExamination(examRes.data)
      
      // Загружаем профпатологов
      const orgsRes = await organizationsAPI.list()
      const clinic = (orgsRes.data.results || orgsRes.data).find(
        (o: any) => o.id === examRes.data.clinic && o.org_type === 'clinic'
      )
      // TODO: Загрузить профпатологов через API
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleComplete = async () => {
    if (!examination || profpathologists.length === 0) return

    try {
      await examinationsAPI.complete(
        examination.id,
        finalResult,
        profpathologists[0].id
      )
      alert('Осмотр завершен!')
      loadData()
      setShowCompleteForm(false)
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка завершения осмотра')
    }
  }

  if (!isAuthenticated || loading) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Button variant="outline" onClick={() => router.back()} className="mb-6">
          ← Назад
        </Button>

        {examination && (
          <>
            <Card className="mb-6">
              <h1 className="text-2xl font-bold mb-4">Детали осмотра</h1>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Сотрудник</p>
                  <p className="font-semibold">{examination.employee_info?.full_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Должность</p>
                  <p className="font-semibold">{examination.employee_info?.position_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Работодатель</p>
                  <p className="font-semibold">{examination.employer_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Клиника</p>
                  <p className="font-semibold">{examination.clinic_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Статус</p>
                  <p className="font-semibold">
                    {examination.status === 'scheduled' ? 'Запланирован' :
                     examination.status === 'in_progress' ? 'В процессе' :
                     examination.status === 'completed' ? 'Завершен' :
                     'Отменен'}
                  </p>
                </div>
                {examination.result && (
                  <div>
                    <p className="text-sm text-gray-600">Результат</p>
                    <p className="font-semibold">
                      {examination.result === 'fit' ? 'Годен' :
                       examination.result === 'unfit' ? 'Не годен' :
                       'Годен с ограничениями'}
                    </p>
                  </div>
                )}
              </div>
            </Card>

            {examination.doctor_examinations && examination.doctor_examinations.length > 0 && (
              <Card className="mb-6">
                <h2 className="text-xl font-semibold mb-4">Результаты осмотров врачей</h2>
                <div className="space-y-4">
                  {examination.doctor_examinations.map((exam: any) => (
                    <div key={exam.id} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-semibold">{exam.harmful_factor_name}</p>
                          <p className="text-sm text-gray-600">{exam.doctor_specialization}</p>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded ${
                          exam.result === 'fit' ? 'bg-green-100 text-green-800' :
                          exam.result === 'unfit' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {exam.result === 'fit' ? 'Годен' :
                           exam.result === 'unfit' ? 'Не годен' :
                           'С ограничениями'}
                        </span>
                      </div>
                      {exam.findings && (
                        <p className="text-sm text-gray-700 mb-2">{exam.findings}</p>
                      )}
                      {exam.recommendations && (
                        <p className="text-sm text-gray-600 italic">{exam.recommendations}</p>
                      )}
                      {exam.contraindications_found && exam.contraindications_found.length > 0 && (
                        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                          <p className="text-xs font-semibold text-red-900 mb-1">Противопоказания:</p>
                          {exam.contraindications_found.map((c: any) => (
                            <p key={c.id} className="text-xs text-red-800">{c.condition}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {examination.status === 'in_progress' && examination.progress?.is_complete && (
              <Card>
                <h2 className="text-xl font-semibold mb-4">Завершение осмотра</h2>
                {!showCompleteForm ? (
                  <Button onClick={() => setShowCompleteForm(true)}>
                    Вынести финальное заключение
                  </Button>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Финальный результат *
                      </label>
                      <div className="grid grid-cols-3 gap-2">
                        <button
                          type="button"
                          onClick={() => setFinalResult('fit')}
                          className={`p-3 rounded-lg border-2 transition-colors ${
                            finalResult === 'fit'
                              ? 'border-green-500 bg-green-50'
                              : 'border-gray-300'
                          }`}
                        >
                          <CheckCircle className="w-6 h-6 text-green-600 mx-auto mb-1" />
                          <span className="text-sm">Годен</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setFinalResult('limited')}
                          className={`p-3 rounded-lg border-2 transition-colors ${
                            finalResult === 'limited'
                              ? 'border-yellow-500 bg-yellow-50'
                              : 'border-gray-300'
                          }`}
                        >
                          <AlertCircle className="w-6 h-6 text-yellow-600 mx-auto mb-1" />
                          <span className="text-sm">С ограничениями</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setFinalResult('unfit')}
                          className={`p-3 rounded-lg border-2 transition-colors ${
                            finalResult === 'unfit'
                              ? 'border-red-500 bg-red-50'
                              : 'border-gray-300'
                          }`}
                        >
                          <XCircle className="w-6 h-6 text-red-600 mx-auto mb-1" />
                          <span className="text-sm">Не годен</span>
                        </button>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleComplete}>Завершить осмотр</Button>
                      <Button variant="outline" onClick={() => setShowCompleteForm(false)}>
                        Отмена
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
            )}

            {examination.status === 'completed' && (
              <Card className="bg-green-50 border-green-200">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                  <div>
                    <h3 className="font-semibold text-green-900">Осмотр завершен</h3>
                    <p className="text-sm text-green-700">
                      Результат: {examination.result === 'fit' ? 'Годен' :
                                  examination.result === 'unfit' ? 'Не годен' :
                                  'Годен с ограничениями'}
                    </p>
                  </div>
                </div>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  )
}

