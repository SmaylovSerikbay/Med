import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { authAPI } from '@/lib/api'

interface Organization {
  id: number
  name: string
  type: 'employer' | 'clinic'
  role: string
}

interface UserProfile {
  user: {
    id: number
    phone_number: string
    phone_verified: boolean
    date_joined: string | null
    first_name?: string
    last_name?: string
    middle_name?: string
  }
  roles: string[]
  primary_role: 'employer' | 'clinic' | 'patient'
  organizations: Organization[]
  employee?: {
    id: number
    employer_id: number
    employer_name: string
    first_name: string
    last_name: string
    middle_name: string
    iin: string
    position_id?: number
    position_name?: string
    department: string
    hire_date?: string
  }
  medical_staff?: {
    organization_id: number
    organization_name: string
    role: string
    specialization?: string
    license_number?: string
  }
}

interface UserState {
  profile: UserProfile | null
  isLoading: boolean
  loadProfile: () => Promise<void>
  clearProfile: () => void
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      profile: null,
      isLoading: false,
      loadProfile: async () => {
        set({ isLoading: true })
        try {
          const response = await authAPI.getProfile()
          set({ profile: response.data, isLoading: false })
        } catch (error) {
          console.error('Ошибка загрузки профиля:', error)
          set({ profile: null, isLoading: false })
        }
      },
      clearProfile: () => {
        set({ profile: null })
      },
    }),
    {
      name: 'user-profile-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)

