'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore, useIsAuthenticated } from '@/store/authStore'
import { Loading } from '@/components/ui/Loading'

export default function Home() {
  const router = useRouter()
  const { _hasHydrated } = useAuthStore()
  const isAuthenticated = useIsAuthenticated()

  useEffect(() => {
    // Ждем пока Zustand восстановит состояние из localStorage
    if (!_hasHydrated) {
      return
    }

    if (isAuthenticated) {
      router.push('/dashboard')
    } else {
      router.push('/login')
    }
  }, [_hasHydrated, isAuthenticated, router])

  // Показываем загрузку пока проверяем аутентификацию
  if (!_hasHydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading />
      </div>
    )
  }

  return null
}

