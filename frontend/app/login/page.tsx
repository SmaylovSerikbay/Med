'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card } from '@/components/ui/Card'
import { PhoneInput } from '@/components/ui/PhoneInput'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { useUserStore } from '@/store/userStore'
import { MessageCircle, Shield, Lock, KeyRound } from 'lucide-react'

type AuthMethod = 'whatsapp' | 'password'
type Step = 'phone' | 'otp' | 'password' | 'reset-otp' | 'reset-confirm'

export default function LoginPage() {
  const router = useRouter()
  const setAuth = useAuthStore((state) => state.setAuth)
  const { loadProfile } = useUserStore()
  const [authMethod, setAuthMethod] = useState<AuthMethod>('whatsapp')
  const [step, setStep] = useState<Step>('phone')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [password, setPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // PhoneInput уже возвращает нормализованный номер
  const isPhoneValid = (phone: string): boolean => {
    return phone.length === 11 && phone.startsWith('7')
  }

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Защита от повторных запросов
    if (isLoading) {
      return
    }

    // Валидация номера
    if (!isPhoneValid(phoneNumber)) {
      setError('Введите корректный номер телефона')
      return
    }
    
    setError('')
    setIsLoading(true)

    try {
      await authAPI.sendOTP(phoneNumber)
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
      const response = await authAPI.verifyOTP(phoneNumber, otpCode)
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

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    // Валидация номера
    if (!isPhoneValid(phoneNumber)) {
      setError('Введите корректный номер телефона')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      const response = await authAPI.loginPassword(phoneNumber, password)
      setAuth(response.data.user, response.data.tokens)
      await loadProfile()
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка входа')
    } finally {
      setIsLoading(false)
    }
  }

  const handleResetPasswordRequest = async (e: React.FormEvent) => {
    e.preventDefault()

    // Валидация номера
    if (!isPhoneValid(phoneNumber)) {
      setError('Введите корректный номер телефона')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      await authAPI.resetPasswordRequest(phoneNumber)
      setSuccess('Код для сброса пароля отправлен на WhatsApp')
      setStep('reset-otp')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка отправки кода')
    } finally {
      setIsLoading(false)
    }
  }

  const handleResetPasswordConfirm = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await authAPI.resetPasswordConfirm(phoneNumber, otpCode, newPassword)
      setSuccess('Пароль успешно изменен! Войдите с новым паролем')
      setTimeout(() => {
        setStep('password')
        setAuthMethod('password')
        setOtpCode('')
        setNewPassword('')
        setSuccess('')
      }, 2000)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка сброса пароля')
    } finally {
      setIsLoading(false)
    }
  }

  const switchAuthMethod = (method: AuthMethod) => {
    setAuthMethod(method)
    setStep(method === 'whatsapp' ? 'phone' : 'password')
    setError('')
    setSuccess('')
    setPassword('')
    setOtpCode('')
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
          {/* Переключатель методов авторизации */}
          {(step === 'phone' || step === 'password') && (
            <div className="flex gap-2 mb-6 p-1 bg-gray-100 rounded-lg">
              <button
                type="button"
                onClick={() => switchAuthMethod('whatsapp')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  authMethod === 'whatsapp'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <MessageCircle className="w-4 h-4 inline mr-2" />
                WhatsApp
              </button>
              <button
                type="button"
                onClick={() => switchAuthMethod('password')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  authMethod === 'password'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Lock className="w-4 h-4 inline mr-2" />
                Пароль
              </button>
            </div>
          )}

          {/* WhatsApp OTP - Ввод телефона */}
          {step === 'phone' && authMethod === 'whatsapp' && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Вход через WhatsApp
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Введите номер телефона, и мы отправим код подтверждения в WhatsApp
                </p>
              </div>

              <PhoneInput
                label="Номер телефона"
                value={phoneNumber}
                onChange={setPhoneNumber}
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
          )}

          {/* WhatsApp OTP - Ввод кода */}
          {step === 'otp' && (
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

          {/* Вход по паролю */}
          {step === 'password' && (
            <form onSubmit={handlePasswordLogin} className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Вход по паролю
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Введите номер телефона и пароль
                </p>
              </div>

              <PhoneInput
                label="Номер телефона"
                value={phoneNumber}
                onChange={setPhoneNumber}
                required
                disabled={isLoading}
              />

              <Input
                label="Пароль"
                type="password"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
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
                disabled={!phoneNumber || !password}
              >
                <Lock className="w-4 h-4 mr-2" />
                Войти
              </Button>

              <button
                type="button"
                onClick={() => {
                  setStep('phone')
                  setAuthMethod('whatsapp')
                  setPhoneNumber('')
                  setPassword('')
                  setError('')
                }}
                className="w-full text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Забыли пароль? Войдите через WhatsApp
              </button>
            </form>
          )}

          {/* Сброс пароля - Запрос кода */}
          {step === 'reset-otp' && (
            <form onSubmit={(e) => {
              e.preventDefault()
              // Код уже отправлен, переходим к подтверждению
              setStep('reset-confirm')
            }} className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Введите код из WhatsApp
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Код отправлен на {phoneNumber}
                </p>
              </div>

              {success && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
                  {success}
                </div>
              )}

              <Input
                label="Код подтверждения"
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
                    setStep('password')
                    setOtpCode('')
                    setError('')
                    setSuccess('')
                  }}
                  disabled={isLoading}
                >
                  Назад
                </Button>
                <Button
                  type="submit"
                  className="flex-1"
                  disabled={otpCode.length !== 6}
                >
                  Далее
                </Button>
              </div>
            </form>
          )}

          {/* Сброс пароля - Новый пароль */}
          {step === 'reset-confirm' && (
            <form onSubmit={handleResetPasswordConfirm} className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Установите новый пароль
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Минимум 6 символов
                </p>
              </div>

              <Input
                label="Новый пароль"
                type="password"
                placeholder="Минимум 6 символов"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                error={error}
                disabled={isLoading}
              />

              {success && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
                  {success}
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setStep('reset-otp')
                    setNewPassword('')
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
                  disabled={newPassword.length < 6}
                >
                  Сохранить
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

