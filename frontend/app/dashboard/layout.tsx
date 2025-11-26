'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore, useIsAuthenticated } from '@/store/authStore'
import { Header } from '@/components/layout/Header'
import { Loading } from '@/components/ui/Loading'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { _hasHydrated, accessToken } = useAuthStore()
  const isAuthenticated = useIsAuthenticated()
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    // Ждем пока Zustand восстановит состояние из localStorage
    if (!_hasHydrated) {
      return
    }

    // Проверяем наличие токена
    const token = accessToken || (typeof window !== 'undefined' ? localStorage.getItem('access_token') : null)
    
    if (!token) {
      router.push('/login')
    } else {
      setIsChecking(false)
    }
  }, [_hasHydrated, accessToken, router])

  // Показываем загрузку пока проверяем аутентификацию
  if (!_hasHydrated || isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <>
      <Header />
      {children}
    </>
  )
}

