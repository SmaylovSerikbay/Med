import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface User {
  id: number
  phone_number: string
  phone_verified: boolean
  date_joined: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  _hasHydrated: boolean
  setHasHydrated: (state: boolean) => void
  setAuth: (user: User, tokens: { access: string; refresh: string }) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      _hasHydrated: false,
      setHasHydrated: (state) => {
        set({ _hasHydrated: state })
        // Синхронизируем токены с localStorage для axios interceptor
        if (state && typeof window !== 'undefined') {
          const { accessToken, refreshToken } = get()
          if (accessToken) {
            localStorage.setItem('access_token', accessToken)
          }
          if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken)
          }
        }
      },
      setAuth: (user, tokens) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', tokens.access)
          localStorage.setItem('refresh_token', tokens.refresh)
        }
        set({
          user,
          accessToken: tokens.access,
          refreshToken: tokens.refresh,
        })
      },
      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
        })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        // Синхронизируем токены после восстановления
        if (state && typeof window !== 'undefined') {
          if (state.accessToken) {
            localStorage.setItem('access_token', state.accessToken)
          }
          if (state.refreshToken) {
            localStorage.setItem('refresh_token', state.refreshToken)
          }
        }
        state?.setHasHydrated(true)
      },
    }
  )
)

// Вычисляемое свойство для проверки аутентификации
export const useIsAuthenticated = () => {
  const { accessToken, _hasHydrated } = useAuthStore()
  // Возвращаем false пока не загрузилось состояние из localStorage
  if (!_hasHydrated) return false
  return !!accessToken
}

