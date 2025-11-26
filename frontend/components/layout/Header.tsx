'use client'

import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore, useIsAuthenticated } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { formatPhoneNumber } from '@/lib/phoneUtils'
import { Shield, LogOut, Menu, X, Settings } from 'lucide-react'
import { useState } from 'react'

export function Header() {
  const router = useRouter()
  const pathname = usePathname()
  const { user, logout } = useAuthStore()
  const { profile } = useUserStore()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  // Навигация в зависимости от роли
  const getNavItems = () => {
    if (!profile) return []
    
    const { primary_role } = profile
    
    if (primary_role === 'employer') {
      return [
        { label: 'Главная', path: '/dashboard' },
        { label: 'Сотрудники', path: '/dashboard/employees' },
        { label: 'Осмотры', path: '/dashboard/examinations' },
        { label: 'Календарные планы', path: '/dashboard/calendar-plans' },
        { label: 'Партнерства', path: '/dashboard/partnerships' },
        { label: 'Подписки', path: '/dashboard/subscriptions' },
      ]
    }
    
    if (primary_role === 'clinic') {
      const isClinicOwner = profile.roles.includes('clinic_owner')
      const clinicOrg = profile.organizations.find(o => o.type === 'clinic')
      const userRole = clinicOrg?.role || 'doctor'
      
      const items = [
        { label: 'Главная', path: '/dashboard' },
        { label: 'Осмотры', path: '/dashboard/examinations' },
      ]
      
      // Регистратура только для регистраторов и владельцев
      if (userRole === 'registrar' || isClinicOwner) {
        items.splice(1, 0, { label: 'Регистратура', path: '/dashboard/clinic/registry' })
      }
      
      // Административные функции только для владельцев
      if (isClinicOwner) {
        items.push(
          { label: 'Партнерства', path: '/dashboard/partnerships' },
          { label: 'Документы', path: '/dashboard/documents' },
          { label: 'Медработники', path: '/dashboard/clinic/staff' },
          { label: 'Подписки', path: '/dashboard/subscriptions' }
        )
      }
      
      return items
    }
    
    // Пациент или новый пользователь
    return [
      { label: 'Главная', path: '/dashboard' },
      { label: 'Мои осмотры', path: '/dashboard/examinations' },
      { label: 'Подписки', path: '/dashboard/subscriptions' },
    ]
  }
  
  const navItems = getNavItems()

  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-gray-200/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            <div 
              className="flex items-center gap-3 cursor-pointer group"
              onClick={() => router.push('/dashboard')}
            >
              <div className="p-2 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl group-hover:shadow-glow transition-all duration-300">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-gradient">
                ProfMed
              </h1>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.path
              return (
              <button
                key={item.path}
                onClick={() => router.push(item.path)}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-all duration-200 ${
                    isActive
                      ? 'text-primary-700 bg-primary-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
              >
                {item.label}
              </button>
              )
            })}
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gray-100/80 rounded-xl">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-gray-700">
                {formatPhoneNumber(user?.phone_number || '')}
              </span>
            </div>
            <button
              onClick={() => router.push('/dashboard/settings')}
              className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-200"
              title="Настройки"
            >
              <Settings className="w-5 h-5" />
            </button>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all duration-200"
              title="Выйти"
            >
              <LogOut className="w-5 h-5" />
            </button>

            {/* Mobile menu button */}
            <button
              className="md:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-xl transition-all duration-200"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden pb-4 border-t border-gray-200/60 pt-4 animate-fade-in">
            <div className="flex flex-col gap-1">
              {navItems.map((item) => {
                const isActive = pathname === item.path
                return (
                <button
                  key={item.path}
                  onClick={() => {
                    router.push(item.path)
                    setMobileMenuOpen(false)
                  }}
                    className={`text-left px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                      isActive
                        ? 'text-primary-700 bg-primary-50'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                >
                  {item.label}
                </button>
                )
              })}
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}

