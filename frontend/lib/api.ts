import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем токен к запросам (кроме публичных endpoints)
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    // Не добавляем токен для публичных endpoints авторизации
    const publicEndpoints = ['/auth/send-otp/', '/auth/verify-otp/', '/auth/register/']
    const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.includes(endpoint))
    
    if (!isPublicEndpoint) {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      }
    }
  }
  return config
})

// Обработка ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Публичные endpoints не должны вызывать редирект
      const publicEndpoints = ['/auth/send-otp/', '/auth/verify-otp/', '/auth/register/']
      const isPublicEndpoint = publicEndpoints.some(endpoint => error.config?.url?.includes(endpoint))
      
      // Если это не публичный endpoint и мы на защищенной странице, делаем редирект
      if (!isPublicEndpoint && typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// API методы
export const authAPI = {
  // WhatsApp OTP
  sendOTP: (phoneNumber: string) =>
    api.post('/auth/send-otp/', { phone_number: phoneNumber }),
  
  verifyOTP: (phoneNumber: string, code: string) =>
    api.post('/auth/verify-otp/', { phone_number: phoneNumber, code }),
  
  // Password authentication
  loginPassword: (phoneNumber: string, password: string) =>
    api.post('/auth/login-password/', { phone_number: phoneNumber, password }),
  
  setPassword: (newPassword: string, currentPassword?: string) =>
    api.post('/auth/set-password/', { new_password: newPassword, current_password: currentPassword }),
  
  // Password reset
  resetPasswordRequest: (phoneNumber: string) =>
    api.post('/auth/reset-password/request/', { phone_number: phoneNumber }),
  
  resetPasswordConfirm: (phoneNumber: string, code: string, newPassword: string) =>
    api.post('/auth/reset-password/confirm/', { phone_number: phoneNumber, code, new_password: newPassword }),
  
  getProfile: () => api.get('/auth/profile/'),
}

export const subscriptionsAPI = {
  getPlans: () => api.get('/subscriptions/plans/'),
  getCurrent: () => api.get('/subscriptions/subscriptions/my_subscriptions/'),
  requestSubscription: (organizationId: number, planId: number) =>
    api.post('/subscriptions/subscriptions/request_subscription/', {
      organization_id: organizationId,
      plan_id: planId,
    }),
  approveSubscription: (subscriptionId: number, durationMonths: number = 1) =>
    api.post(`/subscriptions/subscriptions/${subscriptionId}/approve/`, {
      duration_months: durationMonths,
    }),
}

export const organizationsAPI = {
  list: () => api.get('/organizations/organizations/'),
  create: (data: any) => api.post('/organizations/organizations/', data),
  get: (id: number) => api.get(`/organizations/organizations/${id}/`),
  update: (id: number, data: any) => api.put(`/organizations/organizations/${id}/`, data),
  delete: (id: number) => api.delete(`/organizations/organizations/${id}/`),
  getAllClinics: () => api.get('/organizations/organizations/all_clinics/'),
  addMember: (
    id: number, 
    phoneNumber: string, 
    role: string, 
    specialization?: string, 
    licenseNumber?: string,
    firstName?: string,
    lastName?: string,
    middleName?: string
  ) =>
    api.post(`/organizations/organizations/${id}/add_member/`, {
      phone_number: phoneNumber,
      role,
      specialization: specialization || '',
      license_number: licenseNumber || '',
      first_name: firstName || '',
      last_name: lastName || '',
      middle_name: middleName || '',
    }),
  getMembers: (id: number) => api.get(`/organizations/organizations/${id}/members/`),
}

export const employeesAPI = {
  list: () => api.get('/organizations/employees/'),
  create: (data: any) => api.post('/organizations/employees/', data),
  get: (id: number) => api.get(`/organizations/employees/${id}/`),
  update: (id: number, data: any) => api.put(`/organizations/employees/${id}/`, data),
  delete: (id: number) => api.delete(`/organizations/employees/${id}/`),
  importExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/organizations/employees/import_excel/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const complianceAPI = {
  factors: {
    list: () => api.get('/compliance/factors/'),
    get: (id: number) => api.get(`/compliance/factors/${id}/`),
  },
  professions: {
    list: () => api.get('/compliance/professions/'),
    get: (id: number) => api.get(`/compliance/professions/${id}/`),
    autoMapFactors: (professionName: string) =>
      api.post('/compliance/professions/auto_map_factors/', { profession_name: professionName }),
  },
  contraindications: {
    list: (harmfulFactorId?: number) => {
      const params = harmfulFactorId ? { harmful_factor_id: harmfulFactorId } : {}
      return api.get('/compliance/contraindications/', { params })
    },
  },
}

export const examinationsAPI = {
  list: () => api.get('/examinations/examinations/'),
  create: (data: any) => api.post('/examinations/examinations/', data),
  get: (id: number) => api.get(`/examinations/examinations/${id}/`),
  start: (id: number) => api.post(`/examinations/examinations/${id}/start/`),
  addDoctorExamination: (id: number, data: any) =>
    api.post(`/examinations/examinations/${id}/add_doctor_examination/`, data),
  complete: (id: number, result: string, profpathologistId: number) =>
    api.post(`/examinations/examinations/${id}/complete/`, { result, profpathologist_id: profpathologistId }),
  byQr: (qrCode: string) => api.get('/examinations/examinations/by_qr/', { params: { qr_code: qrCode } }),
}

export const documentsAPI = {
  list: () => api.get('/documents/documents/'),
  get: (id: number) => api.get(`/documents/documents/${id}/`),
  getOrGenerateAppendix3: (employerId: number, year: number) =>
    api.get('/documents/documents/get_or_generate_appendix_3/', { params: { employer_id: employerId, year } }),
  generateAppendix3: (employerId: number, year: number) =>
    api.post('/documents/documents/generate_appendix_3/', { employer_id: employerId, year }),
  generateCalendarPlan: (employerId: number, clinicId: number, year: number, startDate: string, endDate?: string) =>
    api.post('/documents/documents/generate_calendar_plan/', {
      employer_id: employerId,
      clinic_id: clinicId,
      year,
      start_date: startDate,
      end_date: endDate,
    }),
  generateFinalAct: (employerId: number, clinicId: number, year: number) =>
    api.post('/documents/documents/generate_final_act/', {
      employer_id: employerId,
      clinic_id: clinicId,
      year,
    }),
  requestSignature: (id: number, role: string) =>
    api.post(`/documents/documents/${id}/request_signature/`, { role }),
  verifyAndSign: (id: number, role: string, otpCode: string) =>
    api.post(`/documents/documents/${id}/verify_and_sign/`, { role, otp_code: otpCode }),
}

export const calendarPlansAPI = {
  list: () => api.get('/documents/calendar-plans/'),
  get: (id: number) => api.get(`/documents/calendar-plans/${id}/`),
  update: (id: number, data: any) => api.put(`/documents/calendar-plans/${id}/`, data),
  partialUpdate: (id: number, data: any) => api.patch(`/documents/calendar-plans/${id}/`, data),
}

export const partnershipsAPI = {
  list: () => api.get('/organizations/partnerships/'),
  get: (id: number) => api.get(`/organizations/partnerships/${id}/`),
  requestPartnership: (employerId: number, clinicId: number, defaultPrice: number = 0) =>
    api.post('/organizations/partnerships/request_partnership/', {
      employer_id: employerId,
      clinic_id: clinicId,
      default_price: defaultPrice,
    }),
  availableClinics: (employerId: number) => api.get('/organizations/partnerships/available_clinics/', { params: { employer_id: employerId } }),
  partnerEmployers: () => api.get('/organizations/partnerships/partner_employers/'),
  confirm: (id: number, pricing: any = {}, defaultPrice: number = 0, notes: string = '', expiresAt?: string) =>
    api.post(`/organizations/partnerships/${id}/confirm/`, {
      pricing,
      default_price: defaultPrice,
      notes,
      expires_at: expiresAt,
    }),
  reject: (id: number) => api.post(`/organizations/partnerships/${id}/reject/`),
}
