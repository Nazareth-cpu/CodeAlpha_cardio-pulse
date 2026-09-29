import React from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  hasDot?: boolean;
}

export function Badge({
  className,
  variant = 'default',
  size = 'md',
  hasDot = false,
  children,
  ...props
}: BadgeProps) {
  const variants = {
    default: 'bg-[#E6F3EF] text-[#087F5B] border-[#087F5B]/20',
    success: 'bg-[#ECFDF5] text-[#059669] border-[#059669]/20',
    warning: 'bg-[#FFFBEB] text-[#D97706] border-[#D97706]/20',
    error: 'bg-[#FEF2F2] text-[#DC2626] border-[#DC2626]/20',
    info: 'bg-[#F0F9FF] text-[#0284C7] border-[#0284C7]/20',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  const dots = {
    default: 'bg-[#087F5B]',
    success: 'bg-[#059669]',
    warning: 'bg-[#D97706]',
    error: 'bg-[#DC2626]',
    info: 'bg-[#0284C7]',
    neutral: 'bg-slate-500',
  };

  const sizes = {
    sm: 'text-[10px] px-2 py-0.5 font-medium gap-1',
    md: 'text-xs px-2.5 py-1 font-semibold gap-1.5',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border tracking-wide uppercase',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {hasDot && (
        <span
          className={cn('w-1.5 h-1.5 rounded-full shrink-0 animate-pulse', dots[variant])}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
}
