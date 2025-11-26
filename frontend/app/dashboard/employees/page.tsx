'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { employeesAPI, organizationsAPI, complianceAPI } from '@/lib/api'
import { Users, Plus, Upload, Search } from 'lucide-react'

export default function EmployeesPage() {
  const router = useRouter()
  const isAuthenticated = useIsAuthenticated()
  const [employees, setEmployees] = useState<any[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])
  const [professions, setProfessions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [formData, setFormData] = useState({
    phone_number: '',
    employer: '', // Будет автоматически определен из организаций пользователя
    first_name: '',
    last_name: '',
    middle_name: '',
    iin: '',
    position: '',
    department: '',
    hire_date: new Date().toISOString().split('T')[0],
    position_start_date: '', // Дата начала работы на должности
    date_of_birth: '', // Дата рождения
    gender: '', // Пол: 'male' или 'female'
    notes: '', // Примечание
  })

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    
    // Проверяем роль - только работодатели могут видеть сотрудников
    const { profile, loadProfile } = useUserStore.getState()
    if (!profile) {
      loadProfile().then(() => {
        const updatedProfile = useUserStore.getState().profile
        if (updatedProfile?.primary_role !== 'employer') {
          router.push('/dashboard')
          return
        }
        loadData()
      })
    } else if (profile.primary_role !== 'employer') {
      router.push('/dashboard')
      return
    } else {
      loadData()
    }
  }, [isAuthenticated, router])

  const loadData = async () => {
    try {
      const [employeesRes, orgsRes, profsRes] = await Promise.all([
        employeesAPI.list(),
        organizationsAPI.list(),
        complianceAPI.professions.list(),
      ])
      setEmployees(employeesRes.data.results || employeesRes.data)
      const employerOrgs = (orgsRes.data.results || orgsRes.data).filter((o: any) => o.org_type === 'employer')
      setOrganizations(employerOrgs)
      
      // Автоматически выбираем первого работодателя если есть только один
      if (employerOrgs.length === 1 && !formData.employer) {
        setFormData(prev => ({ ...prev, employer: String(employerOrgs[0].id) }))
      }
      
      setProfessions(profsRes.data.results || profsRes.data)
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // Подготавливаем данные для отправки
      const dataToSend: any = {
        phone_number: formData.phone_number,
        first_name: formData.first_name,
        last_name: formData.last_name,
        middle_name: formData.middle_name || '',
        iin: formData.iin || '',
        department: formData.department || '',
        hire_date: formData.hire_date,
      }
      
      // Добавляем employer только если указан
      if (formData.employer) {
        dataToSend.employer = parseInt(formData.employer)
      }
      
      // Добавляем position только если указана
      if (formData.position) {
        dataToSend.position = parseInt(formData.position)
      }
      
      // Добавляем новые поля из Формы 3
      if (formData.position_start_date) {
        dataToSend.position_start_date = formData.position_start_date
      }
      if (formData.date_of_birth) {
        dataToSend.date_of_birth = formData.date_of_birth
      }
      if (formData.gender) {
        dataToSend.gender = formData.gender
      }
      if (formData.notes) {
        dataToSend.notes = formData.notes
      }
      
      console.log('Отправка данных сотрудника:', dataToSend)
      
      await employeesAPI.create(dataToSend)
      setShowCreateForm(false)
      setFormData({
        phone_number: '',
        employer: '',
        first_name: '',
        last_name: '',
        middle_name: '',
        iin: '',
        position: '',
        department: '',
        hire_date: new Date().toISOString().split('T')[0],
      })
      loadData()
      alert('Сотрудник успешно добавлен!')
    } catch (error: any) {
      console.error('Ошибка создания сотрудника:', error)
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail || 
                          (typeof error.response?.data === 'object' ? JSON.stringify(error.response.data) : 'Ошибка создания сотрудника')
      alert(`Ошибка создания сотрудника: ${errorMessage}`)
    }
  }

  const handleAutoMapFactors = async (professionName: string) => {
    try {
      const response = await complianceAPI.professions.autoMapFactors(professionName)
      if (response.data.found) {
        alert(`Найдено факторов: ${response.data.factors.length}`)
      } else {
        alert('Факторы не найдены автоматически')
      }
    } catch (error) {
      console.error('Ошибка авто-маппинга:', error)
    }
  }

  const filteredEmployees = employees.filter((emp) => {
    const fullName = `${emp.last_name} ${emp.first_name} ${emp.middle_name}`.toLowerCase()
    return fullName.includes(searchTerm.toLowerCase()) ||
           emp.position_name?.toLowerCase().includes(searchTerm.toLowerCase())
  })

  if (!isAuthenticated) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Сотрудники</h1>
            <p className="text-gray-600 mt-2">Управление сотрудниками организации</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Upload className="w-4 h-4 mr-2" />
              Импорт Excel
            </Button>
            <Button onClick={() => setShowCreateForm(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Добавить сотрудника
            </Button>
          </div>
        </div>

        <div className="mb-6">
          <Input
            placeholder="Поиск по имени или должности..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
          />
        </div>

        {showCreateForm && (
          <Card className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Новый сотрудник</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Номер телефона"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  required
                />
                {organizations.length > 1 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Работодатель *
                    </label>
                    <select
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      value={formData.employer}
                      onChange={(e) => setFormData({ ...formData, employer: e.target.value })}
                      required
                    >
                      <option value="">Выберите работодателя</option>
                      {organizations.map((org) => (
                        <option key={org.id} value={org.id}>{org.name}</option>
                      ))}
                    </select>
                  </div>
                )}
                {organizations.length === 1 && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">
                      <strong>Работодатель:</strong> {organizations[0].name}
                    </p>
                  </div>
                )}
                <Input
                  label="Фамилия"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  required
                />
                <Input
                  label="Имя"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  required
                />
                <Input
                  label="Отчество"
                  value={formData.middle_name}
                  onChange={(e) => setFormData({ ...formData, middle_name: e.target.value })}
                />
                <Input
                  label="ИИН"
                  value={formData.iin}
                  onChange={(e) => setFormData({ ...formData, iin: e.target.value })}
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Должность *
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    value={formData.position}
                    onChange={(e) => {
                      setFormData({ ...formData, position: e.target.value })
                      const profession = professions.find((p) => p.id === parseInt(e.target.value))
                      if (profession) {
                        handleAutoMapFactors(profession.name)
                      }
                    }}
                    required
                  >
                    <option value="">Выберите должность</option>
                    {professions.map((prof) => (
                      <option key={prof.id} value={prof.id}>{prof.name}</option>
                    ))}
                  </select>
                </div>
                <Input
                  label="Отдел/Цех"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                />
                <Input
                  label="Дата приема на работу"
                  type="date"
                  value={formData.hire_date}
                  onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })}
                  required
                />
                <Input
                  label="Дата начала работы на должности"
                  type="date"
                  value={formData.position_start_date}
                  onChange={(e) => setFormData({ ...formData, position_start_date: e.target.value })}
                  helpText="Для расчета стажа по занимаемой должности"
                />
                <Input
                  label="Дата рождения"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  helpText="Можно извлечь из ИИН или указать вручную"
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Пол
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  >
                    <option value="">Не указан</option>
                    <option value="male">Мужской</option>
                    <option value="female">Женский</option>
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Примечание
                  </label>
                  <textarea
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    placeholder="Дополнительная информация о сотруднике"
                  />
                </div>
              </div>
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
        ) : filteredEmployees.length === 0 ? (
          <Card className="text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Нет сотрудников</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredEmployees.map((emp) => (
              <Card
                key={emp.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/dashboard/employees/${emp.id}`)}
              >
                <h3 className="text-lg font-semibold mb-2">{emp.full_name}</h3>
                <p className="text-sm text-gray-600 mb-1">{emp.position_name}</p>
                <p className="text-sm text-gray-600 mb-1">{emp.department}</p>
                <p className="text-sm text-gray-500">{emp.phone_number}</p>
                {emp.harmful_factors && emp.harmful_factors.length > 0 && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-xs text-gray-500 mb-1">Вредные факторы:</p>
                    <div className="flex flex-wrap gap-1">
                      {emp.harmful_factors.slice(0, 3).map((factor: any) => (
                        <span
                          key={factor.id}
                          className="px-2 py-1 text-xs rounded bg-yellow-100 text-yellow-800"
                        >
                          {factor.code}
                        </span>
                      ))}
                      {emp.harmful_factors.length > 3 && (
                        <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-600">
                          +{emp.harmful_factors.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

