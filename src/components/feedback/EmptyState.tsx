import React from 'react';
import { Inbox } from 'lucide-react';
import { Button, type ButtonProps } from '../ui/Button';
import { cn } from '../../lib/utils';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  actionVariant?: ButtonProps['variant'];
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  actionText,
  onAction,
  actionVariant = 'primary',
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-2xl border border-dashed border-slate-200 bg-white/60',
        className,
      )}
    >
      <div className="w-12 h-12 rounded-full bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center mb-4">
        {icon || <Inbox className="w-6 h-6 stroke-[1.5]" />}
      </div>
      <h4 className="text-base font-bold text-[#12231E] tracking-tight">{title}</h4>
      <p className="text-xs text-[#65756F] max-w-sm mt-1.5 leading-relaxed">
        {description}
      </p>
      {actionText && onAction && (
        <div className="mt-5">
          <Button size="sm" variant={actionVariant} onClick={onAction}>
            {actionText}
          </Button>
        </div>
      )}
    </div>
  );
}
