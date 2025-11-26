'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { examinationsAPI, complianceAPI, organizationsAPI } from '@/lib/api'
import { Save, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

export default function DoctorExaminationPage() {
  const router = useRouter()
  const params = useParams()
  const isAuthenticated = useIsAuthenticated()
  const [examination, setExamination] = useState<any>(null)
  const [harmfulFactors, setHarmfulFactors] = useState<any[]>([])
  const [doctors, setDoctors] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [currentFactor, setCurrentFactor] = useState<any>(null)
  const [formData, setFormData] = useState({
    doctor_id: '',
    harmful_factor_id: '',
    result: 'fit',
    findings: '',
    recommendations: '',
  })
  const [contraindications, setContraindications] = useState<any[]>([])

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
      
      // Загружаем факторы сотрудника
      if (examRes.data.employee_info?.harmful_factors) {
        setHarmfulFactors(examRes.data.employee_info.harmful_factors)
        if (examRes.data.employee_info.harmful_factors.length > 0) {
          setCurrentFactor(examRes.data.employee_info.harmful_factors[0])
          setFormData({
            ...formData,
            harmful_factor_id: examRes.data.employee_info.harmful_factors[0].id,
          })
        }
      }
      
      // Загружаем врачей клиники
      const orgsRes = await organizationsAPI.list()
      const clinic = (orgsRes.data.results || orgsRes.data).find(
        (o: any) => o.id === examRes.data.clinic && o.org_type === 'clinic'
      )
      if (clinic) {
        // TODO: Загрузить врачей через API
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCheckContraindications = async () => {
    if (!formData.findings || !currentFactor) return

    try {
      const response = await complianceAPI.contraindications.list(currentFactor.id)
      const allContraindications = response.data.results || response.data
      
      // Простая проверка по тексту
      const found = allContraindications.filter((c: any) =>
        formData.findings.toLowerCase().includes(c.condition.toLowerCase()) ||
        c.condition.toLowerCase().includes(formData.findings.toLowerCase())
      )
      
      setContraindications(found)
    } catch (error) {
      console.error('Ошибка проверки противопоказаний:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await examinationsAPI.addDoctorExamination(Number(params.id), {
        doctor_id: formData.doctor_id,
        harmful_factor_id: formData.harmful_factor_id,
        result: formData.result,
        findings: formData.findings,
        recommendations: formData.recommendations,
      })
      
      alert('Результат осмотра сохранен')
      loadData()
      
      // Очищаем форму для следующего фактора
      const nextFactor = harmfulFactors.find(
        (f) => f.id !== parseInt(formData.harmful_factor_id)
      )
      if (nextFactor) {
        setCurrentFactor(nextFactor)
        setFormData({
          doctor_id: '',
          harmful_factor_id: nextFactor.id,
          result: 'fit',
          findings: '',
          recommendations: '',
        })
        setContraindications([])
      }
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка сохранения результата')
    }
  }

  if (!isAuthenticated || loading) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Осмотр врача</h1>
          {examination && (
            <p className="text-gray-600 mt-2">
              {examination.employee_info?.full_name} - {examination.employee_info?.position_name}
            </p>
          )}
        </div>

        {examination && (
          <Card>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Вредный фактор *
                </label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  value={formData.harmful_factor_id}
                  onChange={(e) => {
                    const factor = harmfulFactors.find((f) => f.id === parseInt(e.target.value))
                    setCurrentFactor(factor)
                    setFormData({ ...formData, harmful_factor_id: e.target.value })
                  }}
                  required
                >
                  <option value="">Выберите фактор</option>
                  {harmfulFactors.map((factor) => (
                    <option key={factor.id} value={factor.id}>
                      {factor.code} - {factor.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Результат осмотра *
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, result: 'fit' })}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      formData.result === 'fit'
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <CheckCircle className="w-6 h-6 text-green-600 mx-auto mb-1" />
                    <span className="text-sm font-medium">Годен</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, result: 'limited' })}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      formData.result === 'limited'
                        ? 'border-yellow-500 bg-yellow-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <AlertTriangle className="w-6 h-6 text-yellow-600 mx-auto mb-1" />
                    <span className="text-sm font-medium">С ограничениями</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, result: 'unfit' })}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      formData.result === 'unfit'
                        ? 'border-red-500 bg-red-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <XCircle className="w-6 h-6 text-red-600 mx-auto mb-1" />
                    <span className="text-sm font-medium">Не годен</span>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Заключение *
                </label>
                <textarea
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={4}
                  value={formData.findings}
                  onChange={(e) => {
                    setFormData({ ...formData, findings: e.target.value })
                    // Автоматическая проверка противопоказаний
                    setTimeout(() => handleCheckContraindications(), 1000)
                  }}
                  placeholder="Введите заключение врача..."
                  required
                />
              </div>

              {contraindications.length > 0 && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h4 className="font-semibold text-red-900 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    Внимание! Обнаружены противопоказания:
                  </h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-red-800">
                    {contraindications.map((c) => (
                      <li key={c.id}>{c.condition} {c.icd_code && `(МКБ-10: ${c.icd_code})`}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Рекомендации
                </label>
                <textarea
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  value={formData.recommendations}
                  onChange={(e) => setFormData({ ...formData, recommendations: e.target.value })}
                  placeholder="Рекомендации врача..."
                />
              </div>

              <div className="flex gap-2">
                <Button type="submit" className="flex-1">
                  <Save className="w-4 h-4 mr-2" />
                  Сохранить результат
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push('/dashboard/clinic/registry')}
                >
                  Назад
                </Button>
              </div>
            </form>
          </Card>
        )}
      </div>
    </div>
  )
}

