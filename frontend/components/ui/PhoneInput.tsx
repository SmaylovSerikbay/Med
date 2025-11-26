'use client'

import { useState, useEffect } from 'react'
import { Phone } from 'lucide-react'

interface PhoneInputProps {
  value: string
  onChange: (value: string) => void
  label?: string
  error?: string
  disabled?: boolean
  required?: boolean
  placeholder?: string
}

export function PhoneInput({
  value,
  onChange,
  label = 'Номер телефона',
  error,
  disabled = false,
  required = false,
  placeholder = '+7 (___) ___-__-__'
}: PhoneInputProps) {
  const [displayValue, setDisplayValue] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  // Форматирование номера для отображения
  const formatPhoneNumber = (phone: string): string => {
    // Убираем все нецифровые символы
    const digits = phone.replace(/\D/g, '')
    
    // Если пусто, возвращаем пустую строку
    if (!digits) return ''
    
    // Форматируем в +7 (XXX) XXX-XX-XX
    let formatted = '+7'
    
    if (digits.length > 1) {
      formatted += ' (' + digits.substring(1, 4)
    }
    if (digits.length >= 4) {
      formatted += ') ' + digits.substring(4, 7)
    }
    if (digits.length >= 7) {
      formatted += '-' + digits.substring(7, 9)
    }
    if (digits.length >= 9) {
      formatted += '-' + digits.substring(9, 11)
    }
    
    return formatted
  }

  // Получение чистого номера (только цифры)
  const getCleanNumber = (phone: string): string => {
    const digits = phone.replace(/\D/g, '')
    // Если начинается с 8, заменяем на 7
    if (digits.startsWith('8')) {
      return '7' + digits.substring(1)
    }
    // Если не начинается с 7, добавляем 7
    if (digits && !digits.startsWith('7')) {
      return '7' + digits
    }
    return digits
  }

  // Валидация номера
  const isValidPhone = (phone: string): boolean => {
    const digits = phone.replace(/\D/g, '')
    return digits.length === 11 && digits.startsWith('7')
  }

  // Обновление отображаемого значения при изменении value
  useEffect(() => {
    if (!isFocused) {
      setDisplayValue(formatPhoneNumber(value))
    }
  }, [value, isFocused])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value
    const digits = input.replace(/\D/g, '')
    
    // Ограничиваем до 11 цифр
    if (digits.length > 11) return
    
    // Форматируем для отображения
    const formatted = formatPhoneNumber(digits)
    setDisplayValue(formatted)
    
    // Отправляем чистый номер родителю
    const cleanNumber = getCleanNumber(digits)
    onChange(cleanNumber)
  }

  const handleFocus = () => {
    setIsFocused(true)
    // Если пусто, добавляем +7
    if (!displayValue) {
      setDisplayValue('+7 ')
    }
  }

  const handleBlur = () => {
    setIsFocused(false)
    // Форматируем финальное значение
    setDisplayValue(formatPhoneNumber(value))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Разрешаем навигационные клавиши
    if (['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab'].includes(e.key)) {
      return
    }
    
    // Разрешаем только цифры
    if (!/^\d$/.test(e.key)) {
      e.preventDefault()
    }
  }

  const isValid = value ? isValidPhone(value) : true
  const showError = error || (!isValid && value && !isFocused)

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Phone className={`w-5 h-5 ${
            showError ? 'text-red-400' : 
            isValid && value ? 'text-green-500' : 
            'text-gray-400'
          }`} />
        </div>
        
        <input
          type="tel"
          value={displayValue}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          className={`
            w-full pl-10 pr-10 py-2.5 
            border rounded-lg 
            text-base
            transition-all duration-200
            ${showError
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
              : isValid && value
              ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
              : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500'
            }
            ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}
            focus:outline-none focus:ring-2 focus:ring-opacity-50
            placeholder:text-gray-400
          `}
        />
        
        {/* Индикатор валидности */}
        {value && !isFocused && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            {isValid ? (
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        )}
      </div>
      
      {/* Сообщения об ошибках или подсказки */}
      {showError ? (
        <p className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error || 'Неверный формат номера телефона'}
        </p>
      ) : value && isValid && !isFocused ? (
        <p className="mt-1.5 text-sm text-green-600 flex items-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          Номер телефона корректен
        </p>
      ) : (
        <p className="mt-1.5 text-sm text-gray-500">
          Формат: +7 (700) 123-45-67
        </p>
      )}
    </div>
  )
}
