/**
 * Утилиты для работы с номерами телефонов
 */

/**
 * Форматирует номер телефона для отображения
 * @param phone - номер телефона (например, "77001234567")
 * @returns отформатированный номер (например, "+7 (700) 123-45-67")
 */
export function formatPhoneNumber(phone: string): string {
  if (!phone) return ''
  
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

/**
 * Нормализует номер телефона (убирает форматирование, добавляет 7)
 * @param phone - номер телефона в любом формате
 * @returns нормализованный номер (например, "77001234567")
 */
export function normalizePhoneNumber(phone: string): string {
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

/**
 * Проверяет валидность номера телефона
 * @param phone - номер телефона
 * @returns true если номер валиден
 */
export function isValidPhoneNumber(phone: string): boolean {
  const digits = phone.replace(/\D/g, '')
  return digits.length === 11 && digits.startsWith('7')
}

/**
 * Маскирует номер телефона для безопасного отображения
 * @param phone - номер телефона
 * @returns замаскированный номер (например, "+7 (700) ***-**-67")
 */
export function maskPhoneNumber(phone: string): string {
  if (!phone) return ''
  
  const digits = phone.replace(/\D/g, '')
  
  if (digits.length < 11) return phone
  
  return `+7 (${digits.substring(1, 4)}) ***-**-${digits.substring(9, 11)}`
}
