'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { organizationsAPI } from '@/lib/api'
import { Building2, Plus, Users, Stethoscope } from 'lucide-react'

export default function OrganizationsPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const { loadProfile } = useUserStore()
  const [organizations, setOrganizations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const searchParams = useSearchParams()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    org_type: 'employer',
    bin: '',
    address: '',
    phone: '',
    email: '',
  })

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    
    // Проверяем параметр из URL для автоматического открытия формы
    const createType = searchParams?.get('create')
    if (createType === 'employer' || createType === 'clinic') {
      setShowCreateForm(true)
      setFormData(prev => ({ ...prev, org_type: createType }))
    }
    
    loadOrganizations()
  }, [isAuthenticated, router, searchParams])

  const loadOrganizations = async () => {
    try {
      const response = await organizationsAPI.list()
      setOrganizations(response.data.results || response.data)
    } catch (error) {
      console.error('Ошибка загрузки организаций:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await organizationsAPI.create(formData)
      const newOrg = response.data
      
      setShowCreateForm(false)
      setFormData({
        name: '',
        org_type: 'employer',
        bin: '',
        address: '',
        phone: '',
        email: '',
      })
      await loadOrganizations()
      
      // Перезагружаем профиль чтобы обновилась роль
      await loadProfile()
      
      // Показываем уведомление о необходимости подписки
      alert(`Организация "${newOrg.name}" создана!\n\nДля доступа к функциям необходимо запросить подписку. Перейдите в раздел "Подписки" для выбора плана.`)
      
      // Перенаправляем на дашборд
      router.push('/dashboard')
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка создания организации')
    }
  }

  if (!isAuthenticated) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Организации</h1>
            <p className="text-gray-600 mt-2">Управление работодателями и клиниками</p>
          </div>
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Создать организацию
          </Button>
        </div>

        {showCreateForm && (
          <Card className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Новая организация</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Название"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Тип организации
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    value={formData.org_type}
                    onChange={(e) => setFormData({ ...formData, org_type: e.target.value })}
                  >
                    <option value="employer">Работодатель</option>
                    <option value="clinic">Клиника</option>
                  </select>
                </div>
                <Input
                  label="БИН"
                  value={formData.bin}
                  onChange={(e) => setFormData({ ...formData, bin: e.target.value })}
                />
                <Input
                  label="Телефон"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
                <Input
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <Input
                label="Адрес"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              />
              <div className="flex gap-2">
                <Button type="submit">Создать</Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateForm(false)}
                >
                  Отмена
                </Button>
              </div>
            </form>
          </Card>
        )}

        {loading ? (
          <div className="text-center py-12">Загрузка...</div>
        ) : organizations.length === 0 ? (
          <Card className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Нет организаций</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {organizations.map((org) => (
              <Card
                key={org.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/dashboard/organizations/${org.id}`)}
              >
                <div className="flex items-start justify-between mb-4">
                  {org.org_type === 'clinic' ? (
                    <Stethoscope className="w-8 h-8 text-blue-600" />
                  ) : (
                    <Building2 className="w-8 h-8 text-green-600" />
                  )}
                  <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">
                    {org.org_type === 'clinic' ? 'Клиника' : 'Работодатель'}
                  </span>
                </div>
                <h3 className="text-lg font-semibold mb-2">{org.name}</h3>
                {org.bin && <p className="text-sm text-gray-600 mb-1">БИН: {org.bin}</p>}
                {org.phone && <p className="text-sm text-gray-600">Телефон: {org.phone}</p>}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

