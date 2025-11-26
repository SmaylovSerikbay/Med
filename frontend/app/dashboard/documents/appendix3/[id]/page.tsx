'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { documentsAPI } from '@/lib/api'
import { ArrowLeft, Download, FileText } from 'lucide-react'

export default function Appendix3ViewPage() {
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

  if (!document || document.document_type !== 'appendix_3') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Документ не найден или не является Приложением 3</p>
            <Button onClick={() => router.push('/dashboard/documents')}>
              Вернуться к документам
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  const employees = document.content?.employees || []

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => router.push('/dashboard/documents')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Назад
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Приложение 3</h1>
              <p className="text-gray-600 mt-1">
                Список лиц, подлежащих обязательному медицинскому осмотру на {document.year} год
              </p>
            </div>
          </div>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Экспорт в Excel
          </Button>
        </div>

        <Card>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-100 border-b-2 border-gray-300">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    №
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    ФИО
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Дата рождения
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Пол
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Объект или участок
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Занимаемая должность
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Общий стаж
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Стаж по занимаемой должности
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Дата последнего медосмотра
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-r border-gray-300">
                    Профессиональная вредность
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                    Примечание
                  </th>
                </tr>
              </thead>
              <tbody>
                {employees.length === 0 ? (
                  <tr>
                    <td colSpan={11} className="px-4 py-8 text-center text-gray-500">
                      Нет сотрудников, подлежащих осмотру
                    </td>
                  </tr>
                ) : (
                  employees.map((emp: any, index: number) => (
                    <tr key={emp.id || index} className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {index + 1}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.full_name || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.date_of_birth ? formatDate(emp.date_of_birth) : '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.gender || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.department || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.position || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.total_experience || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.position_experience || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.last_examination_date ? formatDate(emp.last_examination_date) : '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200">
                        {emp.harmful_factors || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {emp.notes || '-'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">
                Всего сотрудников: <span className="font-semibold">{employees.length}</span>
              </p>
              <p className="text-sm text-gray-500">
                Сформировано: {document.created_at ? formatDate(document.created_at) : '-'}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

