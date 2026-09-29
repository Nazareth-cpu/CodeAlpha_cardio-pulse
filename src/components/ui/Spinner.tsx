import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'xs' | 'sm' | 'md' | 'lg';
  label?: string;
}

export function Spinner({
  className,
  size = 'md',
  label = 'Loading...',
  ...props
}: SpinnerProps) {
  const sizes = {
    xs: 'w-3.5 h-3.5',
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div
      role="status"
      className={cn('inline-flex items-center justify-center text-[#087F5B]', className)}
      {...props}
    >
      <Loader2 className={cn('animate-spin', sizes[size])} aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </div>
  );
}
