'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { examinationsAPI, organizationsAPI } from '@/lib/api'
import { Calendar, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

export default function ExaminationsPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const [examinations, setExaminations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'scheduled' | 'in_progress' | 'completed'>('all')

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    loadExaminations()
  }, [isAuthenticated, router])

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

  if (!isAuthenticated) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Медицинские осмотры</h1>
            <p className="text-gray-600 mt-2">Управление осмотрами сотрудников</p>
          </div>
        </div>

        <div className="flex gap-2 mb-6">
          {(['all', 'scheduled', 'in_progress', 'completed'] as const).map((f) => (
            <Button
              key={f}
              variant={filter === f ? 'primary' : 'outline'}
              onClick={() => setFilter(f)}
            >
              {f === 'all' ? 'Все' :
               f === 'scheduled' ? 'Запланированные' :
               f === 'in_progress' ? 'В процессе' :
               'Завершенные'}
            </Button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">Загрузка...</div>
        ) : filteredExaminations.length === 0 ? (
          <Card className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Нет осмотров</p>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredExaminations.map((exam) => (
              <Card
                key={exam.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/dashboard/examinations/${exam.id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(exam.status)}
                      <h3 className="text-lg font-semibold">
                        {exam.employee_info?.full_name}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded ${getStatusColor(exam.status)}`}>
                        {exam.status === 'scheduled' ? 'Запланирован' :
                         exam.status === 'in_progress' ? 'В процессе' :
                         exam.status === 'completed' ? 'Завершен' :
                         'Отменен'}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Должность:</span> {exam.employee_info?.position_name}
                      </div>
                      <div>
                        <span className="font-medium">Клиника:</span> {exam.clinic_name}
                      </div>
                      <div>
                        <span className="font-medium">Дата:</span>{' '}
                        {new Date(exam.scheduled_date).toLocaleDateString('ru-RU')}
                      </div>
                      {exam.result && (
                        <div>
                          <span className="font-medium">Результат:</span>{' '}
                          {exam.result === 'fit' ? 'Годен' :
                           exam.result === 'unfit' ? 'Не годен' :
                           'С ограничениями'}
                        </div>
                      )}
                    </div>
                    {exam.progress && (
                      <div className="mt-3">
                        <div className="flex justify-between text-sm mb-1">
                          <span>Прогресс осмотра</span>
                          <span>{exam.progress.completed_exams} / {exam.progress.total_doctors}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all"
                            style={{ width: `${exam.progress.progress_percent}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                  {exam.qr_code && (
                    <div className="ml-4 text-center">
                      <div className="p-2 bg-gray-100 rounded">
                        <div className="text-xs text-gray-600 mb-1">QR код</div>
                        <div className="text-xs font-mono">{exam.qr_code.slice(0, 8)}...</div>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

