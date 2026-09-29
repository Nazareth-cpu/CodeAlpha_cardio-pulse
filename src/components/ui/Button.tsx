import React, { forwardRef } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'amber' | 'emerald' | 'teal' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled = false,
      leftIcon,
      rightIcon,
      children,
      type = 'button',
      ...props
    },
    ref,
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-150 cursor-pointer select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none active:scale-[0.98]';

    const variants: Record<string, string> = {
      // PRIMARY CTA: Warm Amber #F4B942, Dark text #12231E
      primary:
        'bg-[#F4B942] hover:bg-[#DE9E27] active:bg-[#C98B1B] text-[#12231E] shadow-sm font-bold border border-[#DE9E27]/40 focus-visible:ring-[#F4B942]',
      amber:
        'bg-[#F4B942] hover:bg-[#DE9E27] active:bg-[#C98B1B] text-[#12231E] shadow-sm font-bold border border-[#DE9E27]/40 focus-visible:ring-[#F4B942]',

      // SECONDARY CTA: Deep Emerald #087F5B, White text
      secondary:
        'bg-[#087F5B] hover:bg-[#066749] active:bg-[#05543c] text-white shadow-sm focus-visible:ring-[#087F5B]',
      emerald:
        'bg-[#087F5B] hover:bg-[#066749] active:bg-[#05543c] text-white shadow-sm focus-visible:ring-[#087F5B]',

      // SUPPORTING HEALTH-TECH: Electric Teal #14B8A6
      teal:
        'bg-[#14B8A6] hover:bg-[#0D9488] active:bg-[#0F766E] text-white shadow-sm focus-visible:ring-[#14B8A6]',

      // TERTIARY: Outlined Emerald/Teal
      outline:
        'border border-[#087F5B]/30 hover:border-[#087F5B] bg-white hover:bg-[#E6F3EF] text-[#087F5B] focus-visible:ring-[#087F5B]',

      ghost:
        'text-[#12231E] hover:bg-[#E6F3EF]/70 hover:text-[#087F5B] focus-visible:ring-[#087F5B]',

      danger:
        'bg-[#EF4444] hover:bg-[#DC2626] text-white shadow-sm focus-visible:ring-[#EF4444]',
    };

    const sizes = {
      sm: 'text-xs px-3 py-1.5 gap-1.5',
      md: 'text-sm px-4.5 py-2.5 gap-2',
      lg: 'text-base px-6 py-3.5 gap-2.5',
    };

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant] || variants.primary, sizes[size], className)}
        {...props}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin shrink-0" aria-hidden="true" />
            <span>Loading...</span>
          </>
        ) : (
          <>
            {leftIcon && <span className="shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="shrink-0">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  },
);

Button.displayName = 'Button';
