import React from 'react'
import { cn } from '@/lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  description?: string
  variant?: 'default' | 'glass' | 'elevated'
}

const Card: React.FC<CardProps> = ({
  children,
  className,
  title,
  description,
  variant = 'default',
  ...props
}) => {
  const variants: Record<string, string> = {
    default: 'bg-white border border-gray-200/60 shadow-soft',
    glass: 'glass shadow-medium',
    elevated: 'bg-white border-0 shadow-large',
  }

  return (
    <div
      className={cn(
        'rounded-2xl p-6 transition-all duration-300',
        variants[variant],
        className
      )}
      {...props}
    >
      {(title || description) && (
        <div className="mb-4">
          {title && (
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
          )}
          {description && (
            <p className="text-sm text-gray-500">{description}</p>
          )}
        </div>
      )}
      {children}
    </div>
  )
}

export { Card }
export default Card

