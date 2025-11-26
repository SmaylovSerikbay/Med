'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { authAPI } from '@/lib/api'
import { useUserStore } from '@/store/userStore'
import { formatPhoneNumber } from '@/lib/phoneUtils'
import { Lock, Check, AlertCircle, Phone } from 'lucide-react'

export default function SettingsPage() {
  const { profile } = useUserStore()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const hasPassword = profile?.user?.has_password

  const handleSetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (newPassword !== confirmPassword) {
      setError('Пароли не совпадают')
      return
    }

    if (newPassword.length < 6) {
      setError('Пароль должен содержать минимум 6 символов')
      return
    }

    setIsLoading(true)

    try {
      await authAPI.setPassword(newPassword, hasPassword ? currentPassword : undefined)
      setSuccess('Пароль успешно установлен')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      
      // Обновляем профиль
      setTimeout(() => {
        window.location.reload()
      }, 1500)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка установки пароля')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Настройки</h1>
        <p className="text-gray-600 mt-1">Управление настройками аккаунта</p>
      </div>

      {/* Информация о пользователе */}
      <Card>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Информация об аккаунте
        </h2>
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-700">Номер телефона</label>
            <div className="flex items-center gap-2 mt-1">
              <Phone className="w-4 h-4 text-gray-400" />
              <p className="text-gray-900 font-medium">
                {formatPhoneNumber(profile?.user?.phone_number || '')}
              </p>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Статус телефона</label>
            <p className="text-gray-900 mt-1">
              {profile?.user?.phone_verified ? (
                <span className="inline-flex items-center text-green-600">
                  <Check className="w-4 h-4 mr-1" />
                  Подтвержден
                </span>
              ) : (
                <span className="text-yellow-600">Не подтвержден</span>
              )}
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Пароль</label>
            <p className="text-gray-900 mt-1">
              {hasPassword ? (
                <span className="inline-flex items-center text-green-600">
                  <Check className="w-4 h-4 mr-1" />
                  Установлен
                </span>
              ) : (
                <span className="text-gray-600">Не установлен</span>
              )}
            </p>
          </div>
        </div>
      </Card>

      {/* Установка/изменение пароля */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Lock className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {hasPassword ? 'Изменить пароль' : 'Установить пароль'}
            </h2>
            <p className="text-sm text-gray-600">
              {hasPassword 
                ? 'Измените пароль для входа в систему'
                : 'Установите пароль для возможности входа без WhatsApp'
              }
            </p>
          </div>
        </div>

        <form onSubmit={handleSetPassword} className="space-y-4">
          {hasPassword && (
            <Input
              label="Текущий пароль"
              type="password"
              placeholder="Введите текущий пароль"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          )}

          <Input
            label="Новый пароль"
            type="password"
            placeholder="Минимум 6 символов"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            disabled={isLoading}
          />

          <Input
            label="Подтвердите новый пароль"
            type="password"
            placeholder="Повторите новый пароль"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            disabled={isLoading}
          />

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
              <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-800">{success}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
            disabled={!newPassword || !confirmPassword || (hasPassword && !currentPassword)}
          >
            {hasPassword ? 'Изменить пароль' : 'Установить пароль'}
          </Button>
        </form>
      </Card>

      {/* Информация о безопасности */}
      <Card>
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Способы входа
        </h2>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start gap-2">
            <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <p>WhatsApp OTP - быстрый вход через код в WhatsApp</p>
          </div>
          {hasPassword && (
            <div className="flex items-start gap-2">
              <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p>Пароль - вход по номеру телефона и паролю</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
