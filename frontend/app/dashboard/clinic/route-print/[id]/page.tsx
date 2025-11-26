'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { examinationsAPI } from '@/lib/api'
import { ArrowLeft, Printer, Download, QrCode, User, Stethoscope } from 'lucide-react'

export default function RoutePrintPage() {
  const router = useRouter()
  const params = useParams()
  const isAuthenticated = useIsAuthenticated()
  const [examination, setExamination] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    loadExamination()
  }, [isAuthenticated, router, params.id])

  const loadExamination = async () => {
    try {
      const response = await examinationsAPI.get(Number(params.id))
      setExamination(response.data)
    } catch (error: any) {
      console.error('Ошибка загрузки осмотра:', error)
      if (error.response?.status === 404) {
        router.push('/dashboard/clinic/registry')
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePrint = () => {
    window.print()
  }

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateStr
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка маршрутного листа...</p>
        </div>
      </div>
    )
  }

  if (!examination || !examination.route) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Маршрутный лист не найден</p>
            <Button onClick={() => router.push('/dashboard/clinic/registry')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Вернуться в регистратуру
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  const route = examination.route
  const doctors = route.doctors_required_info || []
  const completedDoctors = examination.doctor_examinations?.map((de: any) => de.doctor) || []

  return (
    <>
      {/* Controls - скрываются при печати */}
      <div className="no-print bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={() => router.push(`/dashboard/clinic/examination/${examination.id}`)}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Назад к осмотру
            </Button>
            
            <div className="flex gap-2">
              <Button variant="outline" onClick={handlePrint}>
                <Printer className="w-4 h-4 mr-2" />
                Печать
              </Button>
              <Button onClick={() => router.push(`/dashboard/clinic/examination/${examination.id}`)}>
                Продолжить осмотр
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Printable Content */}
      <div className="min-h-screen bg-white py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8 text-center border-b-2 border-gray-800 pb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Индивидуальный маршрутный лист
            </h1>
            <p className="text-gray-600">
              для прохождения обязательного медицинского осмотра
            </p>
          </div>

          {/* Patient Info */}
          <div className="mb-8">
            <Card className="bg-gray-50">
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-4">
                      <User className="w-6 h-6 text-primary-600" />
                      <h2 className="text-xl font-semibold text-gray-900">
                        Данные сотрудника
                      </h2>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500 mb-1">ФИО</p>
                        <p className="font-semibold text-gray-900 text-lg">
                          {examination.employee_info?.full_name || 'Не указано'}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 mb-1">ИИН</p>
                        <p className="font-semibold text-gray-900">
                          {examination.employee_info?.iin || 'Не указан'}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Должность</p>
                        <p className="font-semibold text-gray-900">
                          {examination.employee_info?.position_name || 'Не указана'}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Работодатель</p>
                        <p className="font-semibold text-gray-900">
                          {examination.employer_name || 'Не указан'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* QR Code */}
                  {examination.qr_code && (
                    <div className="ml-6 text-center">
                      <div className="bg-white p-4 rounded-lg border-2 border-gray-300 inline-block">
                        <QrCode className="w-24 h-24 text-gray-800" />
                      </div>
                      <p className="text-xs text-gray-500 mt-2 font-mono">
                        {examination.qr_code.substring(0, 8)}...
                      </p>
                    </div>
                  )}
                </div>

                {/* Examination Info */}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-300">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Дата осмотра</p>
                    <p className="font-semibold text-gray-900">
                      {examination.scheduled_date 
                        ? formatDate(examination.scheduled_date)
                        : 'Не указана'
                      }
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Тип осмотра</p>
                    <p className="font-semibold text-gray-900">
                      {examination.examination_type === 'preliminary' ? 'Предварительный' :
                       examination.examination_type === 'periodic' ? 'Периодический' :
                       'Внеочередной'}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Route List */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Stethoscope className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">
                Маршрут осмотра
              </h2>
            </div>

            {doctors.length === 0 ? (
              <Card>
                <div className="p-6 text-center text-gray-500">
                  Нет назначенных врачей
                </div>
              </Card>
            ) : (
              <div className="space-y-3">
                {doctors.map((doctor: any, index: number) => {
                  const isCompleted = completedDoctors.some((cd: any) => 
                    cd === doctor.id || (typeof cd === 'object' && cd.id === doctor.id)
                  )
                  
                  return (
                    <Card
                      key={doctor.id}
                      className={isCompleted ? 'bg-green-50 border-green-200' : ''}
                    >
                      <div className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className={`
                              w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg
                              ${isCompleted 
                                ? 'bg-green-500 text-white' 
                                : 'bg-gray-200 text-gray-600'
                              }
                            `}>
                              {isCompleted ? '✓' : index + 1}
                            </div>
                            
                            <div>
                              <p className="font-semibold text-gray-900 text-lg">
                                {doctor.specialization || 'Врач'}
                              </p>
                              {doctor.full_name && (
                                <p className="text-sm text-gray-600 mt-1">
                                  {doctor.full_name}
                                </p>
                              )}
                            </div>
                          </div>

                          <div className="text-right">
                            {isCompleted ? (
                              <span className="px-3 py-1 bg-green-500 text-white rounded-full text-sm font-medium">
                                Пройдено
                              </span>
                            ) : (
                              <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-medium">
                                Ожидает
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </Card>
                  )
                })}
              </div>
            )}
          </div>

          {/* Progress */}
          {examination.progress && (
            <div className="mb-8">
              <Card>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Прогресс осмотра</h3>
                    <span className="text-lg font-bold text-primary-600">
                      {examination.progress.progress_percent}%
                    </span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-primary-600 h-4 rounded-full transition-all"
                      style={{ width: `${examination.progress.progress_percent}%` }}
                    ></div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mt-2 text-center">
                    Пройдено {examination.progress.completed_exams} из {examination.progress.total_doctors} врачей
                  </p>
                </div>
              </Card>
            </div>
          )}

          {/* Instructions */}
          <div className="mb-8">
            <Card className="bg-blue-50 border-blue-200">
              <div className="p-6">
                <h3 className="font-semibold text-gray-900 mb-3">Инструкция</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start gap-2">
                    <span className="font-bold">1.</span>
                    <span>Проходите осмотр по порядку указанных врачей</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-bold">2.</span>
                    <span>Предъявляйте QR-код каждому врачу при посещении</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-bold">3.</span>
                    <span>После прохождения всех врачей подойдите к профпатологу для заключения</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-bold">4.</span>
                    <span>Не покидайте клинику до завершения осмотра</span>
                  </li>
                </ul>
              </div>
            </Card>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-300 text-center text-sm text-gray-500">
            <p>Документ сформирован автоматически системой ProfMed.kz</p>
            <p className="mt-1">
              Дата формирования: {new Date().toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          .no-print {
            display: none !important;
          }
          
          body {
            background: white !important;
          }
          
          .min-h-screen {
            min-height: auto !important;
          }
          
          @page {
            margin: 1cm;
          }
        }
      `}</style>
    </>
  )
}

