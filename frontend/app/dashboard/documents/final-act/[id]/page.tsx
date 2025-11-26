'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { documentsAPI } from '@/lib/api'
import { ArrowLeft, Download, Printer, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

export default function FinalActViewPage() {
  const router = useRouter()
  const params = useParams()
  const isAuthenticated = useIsAuthenticated()
  const [document, setDocument] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    loadDocument()
  }, [isAuthenticated, router, params.id])

  const loadDocument = async () => {
    try {
      const response = await documentsAPI.get(Number(params.id))
      setDocument(response.data)
    } catch (error: any) {
      console.error('Ошибка загрузки документа:', error)
      alert('Документ не найден')
      router.push('/dashboard/documents')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-'
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

  const handlePrint = () => {
    window.print()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка документа...</p>
        </div>
      </div>
    )
  }

  if (!document || document.document_type !== 'final_act') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Документ не найден или не является Заключительным актом</p>
            <Button onClick={() => router.push('/dashboard/documents')}>
              Вернуться к документам
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  const content = document.content || {}
  const statistics = content.statistics || {}
  const professionalDiseases = content.professional_diseases || []
  const transferNeeded = content.transfer_needed || []

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between print:hidden">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => router.push('/dashboard/documents')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Назад
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Заключительный акт</h1>
              <p className="text-gray-600 mt-1">
                По результатам периодических медицинских осмотров {document.year} года
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handlePrint}>
              <Printer className="w-4 h-4 mr-2" />
              Печать
            </Button>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Экспорт PDF
            </Button>
          </div>
        </div>

        {/* Document Content */}
        <Card className="print:shadow-none print:border-0">
          <div className="p-8 print:p-0">
            {/* Header */}
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-4">ЗАКЛЮЧИТЕЛЬНЫЙ АКТ</h2>
              <p className="text-lg mb-2">
                по результатам периодических медицинских осмотров {document.year} года
              </p>
              <div className="mt-4 text-sm text-gray-600">
                <p>Работодатель: <span className="font-semibold">{content.employer_name}</span></p>
                <p>Медицинская организация: <span className="font-semibold">{content.clinic_name}</span></p>
              </div>
            </div>

            {/* Statistics */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold mb-4">Статистика осмотров</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="w-5 h-5 text-blue-600" />
                    <p className="text-sm text-gray-600">Всего осмотрено</p>
                  </div>
                  <p className="text-2xl font-bold text-blue-600">{statistics.total_examined || 0}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <p className="text-sm text-gray-600">Годен</p>
                  </div>
                  <p className="text-2xl font-bold text-green-600">{statistics.fit || 0}</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <XCircle className="w-5 h-5 text-red-600" />
                    <p className="text-sm text-gray-600">Не годен</p>
                  </div>
                  <p className="text-2xl font-bold text-red-600">{statistics.unfit || 0}</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                    <p className="text-sm text-gray-600">С ограничениями</p>
                  </div>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.limited || 0}</p>
                </div>
              </div>
            </div>

            {/* Professional Diseases */}
            {professionalDiseases.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold mb-4 text-red-600">
                  Лица с профессиональными заболеваниями
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-red-50 border-b-2 border-red-300">
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-red-200">
                          №
                        </th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-red-200">
                          ФИО
                        </th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                          Должность
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {professionalDiseases.map((item: any, index: number) => (
                        <tr key={item.employee_id || index} className="border-b border-red-100">
                          <td className="px-4 py-3 text-sm text-gray-900 border-r border-red-100">
                            {index + 1}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900 border-r border-red-100">
                            {item.full_name || '-'}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900">
                            {item.position || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Transfer Needed */}
            {transferNeeded.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold mb-4 text-yellow-600">
                  Лица, нуждающиеся в переводе на другую работу
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-yellow-50 border-b-2 border-yellow-300">
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-yellow-200">
                          №
                        </th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-yellow-200">
                          ФИО
                        </th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-yellow-200">
                          Должность
                        </th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                          Рекомендации
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {transferNeeded.map((item: any, index: number) => (
                        <tr key={item.employee_id || index} className="border-b border-yellow-100">
                          <td className="px-4 py-3 text-sm text-gray-900 border-r border-yellow-100">
                            {index + 1}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900 border-r border-yellow-100">
                            {item.full_name || '-'}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900 border-r border-yellow-100">
                            {item.position || '-'}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900">
                            {item.recommendations || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Signatures */}
            <div className="mt-12 pt-8 border-t border-gray-300">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                  <p className="text-sm text-gray-600 mb-2">От работодателя:</p>
                  <div className="border-t-2 border-gray-400 pt-2 mt-16">
                    <p className="text-sm text-gray-600">Подпись</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-2">От медицинской организации:</p>
                  <div className="border-t-2 border-gray-400 pt-2 mt-16">
                    <p className="text-sm text-gray-600">Подпись</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-2">От СЭС:</p>
                  <div className="border-t-2 border-gray-400 pt-2 mt-16">
                    <p className="text-sm text-gray-600">Подпись</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-8 text-sm text-gray-500 text-center">
              <p>Сформировано: {content.generated_at ? formatDate(content.generated_at) : '-'}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

