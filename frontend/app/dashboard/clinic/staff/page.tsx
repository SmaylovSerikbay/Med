'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { organizationsAPI } from '@/lib/api'
import { Users, Plus, Stethoscope, UserCheck, UserX } from 'lucide-react'

export default function ClinicStaffPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const { profile } = useUserStore()
  const [staff, setStaff] = useState<any[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    phone_number: '',
    organization: '',
    role: 'doctor',
    specialization: '',
    license_number: '',
    first_name: '',
    last_name: '',
    middle_name: '',
  })

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    
    // Проверяем роль - только клиники могут управлять медработниками
    if (profile && profile.primary_role !== 'clinic') {
      router.push('/dashboard')
      return
    }
    
    loadData()
  }, [isAuthenticated, router, profile])

  const loadData = async () => {
    try {
      const orgsRes = await organizationsAPI.list()
      const clinicOrgs = (orgsRes.data.results || orgsRes.data).filter((o: any) => o.org_type === 'clinic')
      setOrganizations(clinicOrgs)
      
      // Загружаем медработников для всех клиник пользователя
      const allStaff: any[] = []
      for (const org of clinicOrgs) {
        try {
          const membersRes = await organizationsAPI.getMembers(org.id)
          const members = membersRes.data.results || membersRes.data
          allStaff.push(...members)
        } catch (error) {
          console.error(`Ошибка загрузки медработников для ${org.name}:`, error)
        }
      }
      
      setStaff(allStaff)
      
      // Автоматически выбираем первую клинику если есть только одна
      if (clinicOrgs.length === 1 && !formData.organization) {
        setFormData(prev => ({ ...prev, organization: clinicOrgs[0].id }))
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.organization || !formData.phone_number || !formData.role) {
      alert('Заполните все обязательные поля')
      return
    }

    try {
      await organizationsAPI.addMember(
        parseInt(formData.organization),
        formData.phone_number,
        formData.role,
        formData.specialization,
        formData.license_number,
        formData.first_name,
        formData.last_name,
        formData.middle_name
      )
      alert('Медработник добавлен! Ему будет отправлено уведомление для авторизации.')
      setShowCreateForm(false)
      setFormData({
        phone_number: '',
        organization: formData.organization, // Сохраняем выбранную организацию
        role: 'doctor',
        specialization: '',
        license_number: '',
        first_name: '',
        last_name: '',
        middle_name: '',
      })
      loadData()
    } catch (error: any) {
      alert(error.response?.data?.error || 'Ошибка добавления медработника')
    }
  }

  const getRoleLabel = (role: string) => {
    const roles: Record<string, string> = {
      'doctor': 'Врач',
      'registrar': 'Регистратор',
      'profpathologist': 'Профпатолог',
      'admin': 'Администратор',
    }
    return roles[role] || role
  }

  if (!isAuthenticated || (profile && profile.primary_role !== 'clinic')) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Медработники</h1>
            <p className="text-gray-600 mt-2">Управление медработниками клиники</p>
          </div>
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Добавить медработника
          </Button>
        </div>

        {showCreateForm && (
          <Card className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Новый медработник</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {organizations.length > 1 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Клиника *
                    </label>
                    <select
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      value={formData.organization}
                      onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                      required
                    >
                      <option value="">Выберите клинику</option>
                      {organizations.map((org) => (
                        <option key={org.id} value={org.id}>{org.name}</option>
                      ))}
                    </select>
                  </div>
                )}
                {organizations.length === 1 && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">
                      <strong>Клиника:</strong> {organizations[0].name}
                    </p>
                  </div>
                )}
                <Input
                  label="Фамилия *"
                  placeholder="Иванов"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  required
                />
                <Input
                  label="Имя *"
                  placeholder="Иван"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  required
                />
                <Input
                  label="Отчество"
                  placeholder="Иванович"
                  value={formData.middle_name}
                  onChange={(e) => setFormData({ ...formData, middle_name: e.target.value })}
                />
                <Input
                  label="Номер телефона *"
                  type="tel"
                  placeholder="77001234567"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Роль *
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    required
                  >
                    <option value="doctor">Врач</option>
                    <option value="registrar">Регистратор</option>
                    <option value="profpathologist">Профпатолог</option>
                  </select>
                </div>
                <Input
                  label="Специализация"
                  placeholder="Терапевт, Невролог и т.д."
                  value={formData.specialization}
                  onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                />
                <Input
                  label="Номер лицензии"
                  placeholder="Опционально"
                  value={formData.license_number}
                  onChange={(e) => setFormData({ ...formData, license_number: e.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit">Добавить</Button>
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
        ) : staff.length === 0 ? (
          <Card className="text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Нет медработников</p>
            <p className="text-sm text-gray-500">
              Добавьте медработников чтобы они могли работать в клинике
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {staff.map((member) => (
              <Card key={member.id}>
                <div className="flex items-start justify-between mb-4">
                  <Stethoscope className="w-8 h-8 text-blue-600" />
                  <span className={`px-2 py-1 text-xs rounded ${
                    member.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {member.is_active ? 'Активен' : 'Неактивен'}
                  </span>
                </div>
                <h3 className="text-lg font-semibold mb-2">{member.user_phone}</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <p><strong>Роль:</strong> {getRoleLabel(member.role)}</p>
                  {member.specialization && (
                    <p><strong>Специализация:</strong> {member.specialization}</p>
                  )}
                  {member.license_number && (
                    <p><strong>Лицензия:</strong> {member.license_number}</p>
                  )}
                  <p><strong>Клиника:</strong> {member.organization_name}</p>
                </div>
                <div className="mt-4 pt-4 border-t">
                  <p className="text-xs text-gray-500">
                    Медработник может авторизоваться по номеру телефона и получить доступ к осмотрам клиники
                  </p>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

