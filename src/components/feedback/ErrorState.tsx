import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  retryText?: string;
  className?: string;
}

export function ErrorState({
  title = 'Something went wrong',
  message = 'An unexpected error occurred while communicating with the health intelligence service.',
  onRetry,
  retryText = 'Retry Request',
  className,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={cn(
        'flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-2xl border border-rose-200/80 bg-[#FEF2F2]/50',
        className,
      )}
    >
      <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mb-4">
        <AlertCircle className="w-6 h-6 stroke-[1.75]" />
      </div>
      <h4 className="text-base font-bold text-rose-950 tracking-tight">{title}</h4>
      <p className="text-xs text-rose-800/90 max-w-sm mt-1.5 leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <div className="mt-5">
          <Button
            size="sm"
            variant="outline"
            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
            onClick={onRetry}
            className="border-rose-200 hover:bg-rose-50 text-rose-900"
          >
            {retryText}
          </Button>
        </div>
      )}
    </div>
  );
}
