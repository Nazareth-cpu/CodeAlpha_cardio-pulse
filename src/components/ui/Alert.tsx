import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  description?: string;
  onDismiss?: () => void;
  onClose?: () => void;
}

export function Alert({
  className,
  variant = 'info',
  title,
  description,
  onDismiss,
  onClose,
  children,
  ...props
}: AlertProps) {
  const configs = {
    info: {
      wrapper: 'bg-[#F0F9FF] border-[#BAE6FD] text-[#0369A1]',
      icon: <Info className="w-5 h-5 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />,
    },
    success: {
      wrapper: 'bg-[#ECFDF5] border-[#A7F3D0] text-[#047857]',
      icon: <CheckCircle className="w-5 h-5 text-[#059669] shrink-0 mt-0.5" aria-hidden="true" />,
    },
    warning: {
      wrapper: 'bg-[#FFFBEB] border-[#FDE68A] text-[#B45309]',
      icon: <AlertTriangle className="w-5 h-5 text-[#D97706] shrink-0 mt-0.5" aria-hidden="true" />,
    },
    error: {
      wrapper: 'bg-[#FEF2F2] border-[#FECACA] text-[#B91C1C]',
      icon: <AlertCircle className="w-5 h-5 text-[#DC2626] shrink-0 mt-0.5" aria-hidden="true" />,
    },
  };

  const current = configs[variant];
  const handleDismiss = onDismiss || onClose;

  return (
    <div
      role="alert"
      className={cn(
        'flex items-start gap-3.5 p-4 rounded-xl border text-sm',
        current.wrapper,
        className,
      )}
      {...props}
    >
      {current.icon}
      <div className="flex-1 min-w-0">
        {title && <h5 className="font-semibold text-sm tracking-tight mb-1">{title}</h5>}
        {description && <div className="text-xs leading-relaxed opacity-95">{description}</div>}
        {children && <div className="text-xs leading-relaxed opacity-95">{children}</div>}
      </div>
      {handleDismiss && (
        <button
          type="button"
          onClick={handleDismiss}
          aria-label="Dismiss alert"
          className="p-1 -mr-1 -mt-1 opacity-70 hover:opacity-100 transition-opacity rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-current"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
