'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card } from '@/components/ui/Card'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { MessageCircle, Shield } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const setAuth = useAuthStore((state) => state.setAuth)
  const { loadProfile } = useUserStore()
  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const normalizePhone = (phone: string): string => {
    // Убираем все нецифровые символы
    let normalized = phone.replace(/\D/g, '')
    // Если начинается с 8, заменяем на 7
    if (normalized.startsWith('8')) {
      normalized = '7' + normalized.slice(1)
    }
    // Если не начинается с 7, добавляем 7
    if (!normalized.startsWith('7')) {
      normalized = '7' + normalized
    }
    return normalized
  }

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Защита от повторных запросов
    if (isLoading) {
      return
    }
    
    setError('')
    setIsLoading(true)

    try {
      const normalizedPhone = normalizePhone(phoneNumber)
      await authAPI.sendOTP(normalizedPhone)
      setPhoneNumber(normalizedPhone) // Сохраняем нормализованный номер
      setSuccess('Код отправлен на WhatsApp!')
      setStep('otp')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка отправки кода')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const normalizedPhone = normalizePhone(phoneNumber)
      const response = await authAPI.verifyOTP(normalizedPhone, otpCode)
      setAuth(response.data.user, response.data.tokens)
      // Загружаем профиль с ролями
      await loadProfile()
      router.push('/dashboard')
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.response?.data?.code?.[0] || 'Неверный код'
      setError(errorMessage)
      // Если код неверный или истек, предлагаем запросить новый
      if (errorMessage.includes('истек') || errorMessage.includes('Неверный')) {
        setTimeout(() => {
          setStep('phone')
          setOtpCode('')
        }, 2000)
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ProfMed.kz
          </h1>
          <p className="text-gray-600">
            Цифровая экосистема медицинских осмотров
          </p>
        </div>

        <Card>
          {step === 'phone' ? (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Вход через WhatsApp
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Введите номер телефона, и мы отправим код подтверждения в WhatsApp
                </p>
              </div>

              <Input
                label="Номер телефона"
                type="tel"
                placeholder="77001234567"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
                error={error}
                disabled={isLoading}
              />

              {success && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
                  {success}
                </div>
              )}

              <Button
                type="submit"
                className="w-full"
                isLoading={isLoading}
                disabled={!phoneNumber}
              >
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Отправить код
              </Button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Введите код подтверждения
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Код отправлен на {phoneNumber}
                </p>
              </div>

              <Input
                label="Код из WhatsApp"
                type="text"
                placeholder="123456"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength={6}
                required
                error={error}
                disabled={isLoading}
                className="text-center text-2xl tracking-widest"
              />

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setStep('phone')
                    setOtpCode('')
                    setError('')
                  }}
                  disabled={isLoading}
                >
                  Назад
                </Button>
                <Button
                  type="submit"
                  className="flex-1"
                  isLoading={isLoading}
                  disabled={otpCode.length !== 6}
                >
                  Войти
                </Button>
              </div>
            </form>
          )}
        </Card>

        <p className="text-center text-sm text-gray-500 mt-6">
          Платформа для автоматизации медосмотров согласно Приказу МЗ РК № 131
        </p>
      </div>
    </div>
  )
}

