import React from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'soft'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
}

const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 ease-out focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98]'
  
  const variants: Record<string, string> = {
    primary: 'bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 shadow-lg hover:shadow-xl focus:ring-primary-500/50',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-300',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 focus:ring-gray-300',
    ghost: 'text-gray-700 hover:bg-gray-100/80 focus:ring-gray-300',
    soft: 'bg-primary-50 text-primary-700 hover:bg-primary-100 focus:ring-primary-300',
  }
  
  const sizes: Record<string, string> = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-5 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  }

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Загрузка...
        </>
      ) : (
        children
      )}
    </button>
  )
}

export { Button }
export default Button

