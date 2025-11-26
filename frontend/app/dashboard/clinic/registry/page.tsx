'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { examinationsAPI } from '@/lib/api'
import { QrCode, Search, UserCheck, Printer } from 'lucide-react'

export default function ClinicRegistryPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const [qrCode, setQrCode] = useState('')
  const [examination, setExamination] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleScanQR = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await examinationsAPI.byQr(qrCode)
      setExamination(response.data)
      
      // Автоматически начинаем осмотр если он еще не начат
      if (response.data.status === 'scheduled') {
        await examinationsAPI.start(response.data.id)
        setExamination({ ...response.data, status: 'in_progress' })
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Осмотр не найден')
      setExamination(null)
    } finally {
      setLoading(false)
    }
  }

  const handleStartExamination = async () => {
    if (!examination) return
    
    try {
      await examinationsAPI.start(examination.id)
      setExamination({ ...examination, status: 'in_progress' })
      router.push(`/dashboard/clinic/examination/${examination.id}`)
    } catch (err: any) {
      alert(err.response?.data?.error || 'Ошибка начала осмотра')
    }
  }

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    
    // Только клиники могут использовать регистратуру
    const { profile, loadProfile } = useUserStore.getState()
    if (!profile) {
      loadProfile().then(() => {
        const updatedProfile = useUserStore.getState().profile
        if (updatedProfile?.primary_role !== 'clinic') {
          router.push('/dashboard')
        }
      })
    } else if (profile.primary_role !== 'clinic') {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  const { profile } = useUserStore()
  
  if (!isAuthenticated || (profile && profile.primary_role !== 'clinic')) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Регистратура</h1>
          <p className="text-gray-600 mt-2">Сканирование QR-кода для начала осмотра</p>
        </div>

        <Card>
          <form onSubmit={handleScanQR} className="space-y-4">
            <div className="flex items-center gap-4">
              <QrCode className="w-8 h-8 text-primary-600" />
              <Input
                placeholder="Введите или отсканируйте QR-код"
                value={qrCode}
                onChange={(e) => setQrCode(e.target.value)}
                className="flex-1"
                required
              />
              <Button type="submit" isLoading={loading}>
                <Search className="w-4 h-4 mr-2" />
                Найти
              </Button>
            </div>
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
                {error}
              </div>
            )}
          </form>
        </Card>

        {examination && (
          <Card className="mt-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold mb-2">Информация об осмотре</h2>
                <div className="space-y-2">
                  <p><strong>Сотрудник:</strong> {examination.employee_info?.full_name}</p>
                  <p><strong>Должность:</strong> {examination.employee_info?.position_name}</p>
                  <p><strong>Работодатель:</strong> {examination.employer_name}</p>
                  <p><strong>Тип осмотра:</strong> {
                    examination.examination_type === 'preliminary' ? 'Предварительный' :
                    examination.examination_type === 'periodic' ? 'Периодический' :
                    'Внеочередной'
                  }</p>
                  <p><strong>Статус:</strong> {
                    examination.status === 'scheduled' ? 'Запланирован' :
                    examination.status === 'in_progress' ? 'В процессе' :
                    examination.status === 'completed' ? 'Завершен' :
                    'Отменен'
                  }</p>
                </div>
              </div>
              {examination.status === 'scheduled' && (
                <Button onClick={handleStartExamination}>
                  <UserCheck className="w-4 h-4 mr-2" />
                  Начать осмотр
                </Button>
              )}
              {examination.status === 'in_progress' && (
                <Button onClick={() => router.push(`/dashboard/clinic/examination/${examination.id}`)}>
                  Продолжить осмотр
                </Button>
              )}
            </div>

            {examination.route && examination.route.doctors_required_info && (
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">Маршрутный лист:</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/dashboard/clinic/route-print/${examination.id}`)}
                  >
                    <Printer className="w-4 h-4 mr-2" />
                    Печать
                  </Button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {examination.route.doctors_required_info.map((doctor: any, idx: number) => {
                    const completed = examination.doctor_examinations?.some(
                      (exam: any) => exam.doctor === doctor.id
                    )
                    return (
                      <div
                        key={doctor.id}
                        className={`p-2 rounded ${
                          completed ? 'bg-green-50 border border-green-200' : 'bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          {completed ? (
                            <span className="text-green-600">✓</span>
                          ) : (
                            <span className="text-gray-400">{idx + 1}</span>
                          )}
                          <span className="text-sm">{doctor.specialization}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
                {examination.progress && (
                  <div className="mt-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Прогресс</span>
                      <span>{examination.progress.progress_percent}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all"
                        style={{ width: `${examination.progress.progress_percent}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </Card>
        )}
      </div>
    </div>
  )
}

